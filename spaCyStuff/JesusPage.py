from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding


# new entity label
LABEL = 'ROOM'
LABEL_2 = 'PHONE'

# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
TRAIN_DATA = [

    ("E&T 322 is the computer science office", {
        'entities': [(0, 7, 'ROOM')]
    }),

    ("Which room is Dr.Kangs office", {
        'entities': []
    }),

    ("The senior design room is in E&T B10", {
        'entities': [(29, 36, 'ROOM')]
    }),

    ("The office of Dr.Pamula is E&T A324", {
        'entities': [(27, 35, 'ROOM')]
    }),

    ("Dr.Zilong's office is in E&T A329", {
        'entities': [(25, 33, 'ROOM')]
    }),


    ("Phone (342) 093-4325", {
        'entities': [(6, 20, 'PHONE')]
    }),

    ("Office: E&T A327 Phone: (818) 343-6689 E-mail: zye5@calstatela.edu", {
        'entities': [(8, 16, 'ROOM'), (24, 38, 'PHONE')]
    }),

    ("My phone number is (917) 343-0393", {
        'entities': [(19, 33, 'PHONE')]
    }),

    ("His phone is missing", {
        'entities': []
    })

]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))

def main(model=None, new_model_name='pineapple', output_dir=None, n_iter=10):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    # if model is not None:
    #     nlp = spacy.load('en')
    #     print("Loaded model '%s'" % model)
    # else:
    #     nlp = spacy.blank('en')  # create blank Language class
    #     print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy

    nlp = spacy.load('en_core_web_sm')

    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe('ner')

    ner.add_label(LABEL)   # add new entity label to entity recognizer
    ner.add_label(LABEL_2)
    if model is None:
        optimizer = nlp.begin_training()
    else:
        # Note that 'begin_training' initializes the models, so it'll zero out
        # existing entity types.
        optimizer = nlp.entity.create_optimizer()

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35,
                           losses=losses)
            print('Losses', losses)

    # test the trained model
    #test_text = 'Search Cal State LA:  Search About Cal State LA President Covino News & Information MyCalStateLA Campus Directory Campus Maps Give Now                California State University, Los Angeles        StudentsFuture studentsFaculty & StaffAlumni & GivingCommunity PartnersAcademicsCampus ResourcesAthleticsApply Online    StudentsUndocumented Students Military & Veteran Students Student Government (ASI) Organizations Housing and Residence Life Disability Services Events Leadership University Student Union University Times Golden Eagle Radio  Future studentsAdmissions Apply Online Financial Aid and Scholarships Housing and Residence Life Disability Services International Office Outreach and Recruitment  Faculty & StaffHuman Resources Mgmt Faculty Affairs Academic Senate Center for Effective Teaching and Learning  Alumni & GivingCal State LA Foundation Alumni Association Give to Cal State LA  Community PartnersAcademy of Business Leadership EPIC LACHSA Pasadena Bioscience Collaborative Pat Brown Institute Propel LA Service Learning Stern MASS The School of Arts Enterprise  Academics Campus ResourcesCampus Safety Plan Career Center Children\'s Center Clery Report Commencement Food on Campus Graduation Office Health Center Luckman Fine Arts Complex Privacy Public Safety and Parking Title IX University Auxiliary Services University Bookstore University Internal Auditor University Tutorial Center University Writing Center  Athletics Apply Online    Menu            Zilong Ye       College of Engineering, Computer Science, and Technology        Department of Computer Science     <!--/*--><![CDATA[/* ><!--*/ div.relative {     position: relative;     left: 45px;     border: 0px; }  /*--><!]]>*/   Zilong Ye, Ph.D. Assistant Professor       Department of Computer Science       California State University, Los Angeles       5151 State University Drive, Los Angeles, CA 90032       Office: E&T A327       Phone: (323) 343-6689       E-mail: zye5@calstatela.edu              About Me I am an Assistant Professor in Department of Computer Science, California State University, Los Angeles. I received my Ph.D. degree in Computer Science from University at Buffalo, SUNY in 2015, supervised by Dr. Chunming Qiao. I received my M.S. degree from Shanghai Jiao Tong University in 2010, and my B.S. degree from Shandong University in 2007.   News Our paper on VNF chaining has been accepted by Springer Journal of Cluster Computing.  Research My research interests focus on algorithm and system design in the computer networking areas, including Network Function Virtualization, Software-Defined Networking, Fog Computing, Information-Centric Networking, Cloud Computing, Internet of Things, and Optical Networking.    Publications       2019: C. Galdamez, R. Pamula and Z. Ye, "On Efficient Virtual Network Function Chaining in NFV-based Telecommunications Networks," in Springer Journal of Cluster Computing, 2019.   K. Sawada, M. W. Clark, Z. Ye, N. Alshurafa, and M. Pourhomayoun, “Analyzing the Potential Occurrence of Osteoporosis and Its Correlation to Cardiovascular Disease Using Predictive Analytic,” in IARIA International Journal On Advances in Life Sciences, 2019.       2018: R. Yan, Y. Zhu, D. Li and Z. Ye, “Minimum Cost Seed Set for Threshold Influence Problem under Competitive Models,” Springer Journal of World Wide Web (WWW), 2018. C. DeMatteis, E. Allen, and Z. Ye, "LAunchPad: The Design and Evaluation of a STEM Recruitment Program for Women," in IEEE Frontiers in Education Conference (FIE), 2018. L. Luo, H. Yu and Z. Ye, "Deadline-guaranteed Point-to-Multipoint Bulk Transfers in Inter-Datacenter Networks," in IEEE ICC, 2018.  L. Luo, H. Yu, Z. Ye and X. Du, "Online Deadline-aware Bulk Transfer over Inter-Datacenter WANs," in IEEE INFOCOM, 2018.  J. Sunthonlap, P. Nguyen and Z. Ye, "Intelligent Device Discovery in the Internet of Things - Enabling the Robot Society," https://arxiv.org/abs/1712.08296.  H. Sadadi, D. Aloufi and Z. Ye, "Predict Movie Revenue by Sentimental Analysis of Twitter," in ACM ICDPA, Guangzhou, China, 2018. S. Alharbi, P. Rodriguez, R. Maharaja, P. Iyer, N. Bose and Z. Ye, "FOCUS: A Fog Computing-based Security System for the Internet of Things," in IEEE CCNC workshop on Edge Computing, 2018.  J. Sunthonlap, P. Nguyen, H. Wang, M. Pourhomayoun, Y. Zhu and Z. Ye, "SAND: A Social-Aware and Distributed Scheme for Device Discovery in the Internet of Things," IEEE ICNC, 2018.  H. Wang, A. Balasubramani and Z. Ye, "Optimal Planning of Renewable Generations for Electric Vehicle Charging Station," IEEE ICNC, 2018.           2017: C. Galdamez, R. Pamula and Z. Ye, "Cost-Efficient Virtual Network Function Chaining over NFV-based Telecommunication Networks," in IEEE ANTS, 2017. S. Alharbi, P. Rodriguez, R. Maharaja, P. Iyer, N. Bose and Z. Ye, "Secure the Internet of Things with Challenge Response Authentication in Fog Computing," in IEEE IPCCC, 2017. (poster) G. Zhao, Z. Xu, Z. Ye, K. Wang and J. Wu, "A Load-Balancing Algorithm Based on Key-Link and Resource Contribution Degree for Virtual Optical Networks Mapping," IEEE CITS, 2017. C. Galdamez and Z. Ye, "Resilient Virtual Network Mapping Against Large-scale Regional Failures," IEEE WOCC, 2017. (Invited)  L. Liu, M. Bahrami, Y Peng, L. Xie, A. Ito, S. Mnatsakanyan, G. Qu, Z. Ye, H. Guo, "ICN-FC: An Information-Centric Networking Based Framework for Efficient Functional Chaining," IEEE ICC, 2017.  Z. Ye, Y. Zhu, P. N. Ji, C. Sun and R. Pamula, "Virtual Infrastructure Mapping in Software-Defined Elastic Optical Networks," Springer Photonic Network Communications Journal (PNC), 2017.  M. Bahrami, L. Xie, L. Liu, A. Ito, Y Peng, S. Mnatsakanyan, G. Qu, Z. Ye, H. Guo, "Secure Functional Chaining Enabled by Information-Centric Networking," IEEE ICNC, 2017.         2016: H. Wang, Z. Ye, "Renewable Energy-Aware Demand Response for Distributed Data Centers in Smart Grid," IEEE Green Energy and System Conference (GESC), 2016. A. Guardado, Z. Ye, H. Guo, L. Liu, L. Xie and A. Ito, "NDNWiFi: Named Data Networking enabled WiFi in Challenged Communication Environments," IEEE GLOBECOM workshop on ICN solutions for Real-world Applications 2016. L. Liu, L. Xie, M. Bahrami, Y Peng, A. Ito, S. Mnatsakanyan, G. Qu, Z. Ye, H. Guo, "Demonstration of a Functional Chaining System Enabled by Named-Data Networking," ACM ICN, 2016. (Best Demo Award)  Z. Ye, X. Cao and C. Qiao, "Joint Topology Design and Mapping of Service Function Chains in Network Function Virtualization," IEEE GLOBECOM, 2016. Z. Ye and Philip N. Ji, "Multilayer Virtual Infrastructure Mapping in IP over WDM Networks," IEEE/OSA OECC 2016. Z. Ye, X. Cao, J. Wang, H. Yu and C. Qiao, "Joint Topology Design and Mapping of Service Function Chains for Efficient, Scalable and Reliable Network Function Virtualization," IEEE Network, 2016.        2015: L. Liu, Z. Ye and A. Ito, "CAMS: Coordinator Assisted Mobility Support for Seamless and Bandwidth-Efficient Handover in ICN," IEEE GLOBECOM workshop on ICN solutions for Real-world Applications 2015.  X. Gao, Z. Ye, W. Zhong, Y. Zhao, J. Fan, X. Cao, H. Yu and C. Qiao, "Virtual Network Mapping for Multicast Services with Max-Min Fairness of Reliability," IEEE/OSA Journal of Optical Communications and Networking (JOCN), 2015. X. Gao, W. Zhong, Z. Ye, Y. Zhao, J. Fan, X. Cao, H. Yu and C. Qiao, "Virtual Network Mapping for Reliable Multicast Services with Max-Min Fairness," IEEE GLOBECOM 2015. J. Fan, Z. Ye, C. Guan, X. Gao, K. Ren and C. Qiao, "GREP: Guaranteeing Reliability with Enhanced Protection in NFV," ACM SIGCOMM workshop on HotMiddleBox 2015. S. Shakya, X. Cao, Z. Ye and C. Qiao, "Spectrum Allocation in Spectrum-sliced Elastic Optical Path Networks using Prediction," Springer Photonic Network Communications (PNC), 2015. X. Gao, Z. Ye, C. Qiao, X. Cao, H. Zhang and H. Yu, "Multicast Service-oriented Virtual Network Mapping over Elastic Optical Networks," IEEE ICC 2015.         2014: Z. Ye, A. N. Patel, P. N. Ji and C. Qiao, "Survivable Virtual Infrastructure Mapping with Dedicated Protection in Transport Software-Defined Networks," IEEE/OSA Journal of Optical Communications and Networking (JOCN), 2014. (Invited) W. Tang, X. Yang, J. Li and Z. Ye, "Dynamic Multicast Light-Tree Construction in Intra-Datacenter Networks with Fast Optical Switching," Journal of Internet Technology (JIT), Nov., 2014. S. Shakya, N. Pradhan, X. Cao, Z. Ye and C. Qiao, "Virtual Network Embedding and Reconfiguration in Elastic Optical Networks," IEEE GLOBECOM 2014. Z. Ye, A. N. Patel, P. N. Ji, and C. Qiao, "Distance-Adaptive and Fragmentation-Aware Optical Traffic Grooming in Flexible Grid Optical Networks," IEEE/OSA OECC 2014. Z. Ye, A. N. Patel, P. N. Ji, and C. Qiao, "Root Mean Square (RMS) Factor for Assessing Spectral Fragmentation in Flexible Grid Optical Networks," IEEE/OSA OECC 2014. A. N. Patel, Z. Ye, P. N. Ji and C. Qiao "Survivable Virtual Infrastructure Mapping with Shared Protection in Transport Software-Defined Networks (T-SDNs)," IEEE/OSA OECC 2014. Z. Ye, X. Li, A. N. Patel, P. N. Ji, X. Cao and C. Qiao, "Upgrade-aware Virtual Infrastructure Mapping in Software-Defined Elastic Optical Networks," Springer Photonic Network Communications (PNC), June, 2014. Z. Ye, A. N. Patel, P. N. Ji, and C. Qiao, "Survivable Virtual Infrastructure Mapping over Transport Software-Defined Networks," IEEE/OSA OFC 2014. A. N. Patel, Z. Ye, and P. N. Ji, "Cloud Service Embedding over Software-Defined Flexible Grid Optical Transport Networks," IEEE/OSA OFC 2014. S. Shakya, X. Cao, Z. Ye and C. Qiao, "Spectrum Allocation for Time-varying Traffic in Elastic Optical Networks using Traffic Pattern," IEEE/OSA OFC 2014.         2013: Z. Ye, A. N. Patel, P. N. Ji, C. Qiao and T. Wang, "Virtual Infrastructure Embedding over Software-Defined Flex-grid Optical Networks," IEEE GLOBECOM workshop on SDN on Optics 2013. S. Shakya, Y. Wang, X. Cao, Z. Ye and C. Qiao, "Minimize Sub-carrier Reallocation in Elastic Optical Path Networks using Traffic Prediction," IEEE GLOBECOM 2013. Z. Ye, X. Cao, X. Gao and C. Qiao, "A Predictive and Incremental Grooming Scheme for Time-varying Traffic in WDM Networks," IEEE INFOCOM mini-conference 2013.    Patents Z. Ye L. Liu, and A. Ito, "Packet Handling in Information Centric Networks," US Patent, Application No. 14/845, 206. L. Liu, A. Ito and Z. Ye, "Intelligent Routing in Information Centric Networking," US Patent, Application No. 14/845,151.  Teaching CS1010 - Introduction to Higher Education in Computer Science Majors CS2011 - Introduction to Java Programming CS4440 - Introduction to Operating Systems CS4470 - Computer Networking Protocols CS4471 - Computer Network Configurations and Management CS4963 - Computer Science Recapitulation CS5470 - Advanced Computer Networks Professional Activities Organizing committee:    TPC co-chair of ACM Mobihoc workshop on MobileHealth, 2018 TPC co-chair of the 1st International Symposium on 5G Emerging Technologies, 2017, 2018 Publicity co-chair of the 5th IBM Cloud Academy Conference ICACON 2017 Publicity co-chair of the 2nd IEEE International Conference on Fog and Mobile Edge Computing, 2017 TPC co-chair of the 1st International Workshop on SDN and NFV, 2017, 2018  TPC members:    ICC, GLOBECOM, MobiHoc, WF-5G, BDCloud, HPSR, WOCC, ISCC, ICICS  Journal reviewers:    IEEE Transactions on Network and Service Management IEEE Transactions on Mobile Computing IEEE Transactions on Wireless Communications IEEE Transactions on Communications IEEE Transactions on Vehicular Technology IEEE Transactions on Industrial Informatics IEEE JSAC SI on Game Theory Networks IEEE Communication Magazine IEEE Communication Letters Springer Photonic Network Communications Journal Elsevier Optical Switching and Networking Journal Elsevier Optical Fiber Technology Journal                StudentsUndocumented Students Military & Veteran Students Student Government (ASI) Organizations Housing and Residence Life Disability Services Events Leadership University Student Union University Times Golden Eagle Radio  Future studentsAdmissions Apply Online Financial Aid and Scholarships Housing and Residence Life Disability Services International Office Outreach and Recruitment  Faculty & StaffHuman Resources Mgmt Faculty Affairs Academic Senate Center for Effective Teaching and Learning  Alumni & GivingCal State LA Foundation Alumni Association Give to Cal State LA  Community PartnersAcademy of Business Leadership EPIC LACHSA Pasadena Bioscience Collaborative Pat Brown Institute Propel LA Service Learning Stern MASS The School of Arts Enterprise  Academics Campus ResourcesCampus Safety Plan Career Center Children\'s Center Clery Report Commencement Food on Campus Graduation Office Health Center Luckman Fine Arts Complex Privacy Public Safety and Parking Title IX University Auxiliary Services University Bookstore University Internal Auditor University Tutorial Center University Writing Center  Athletics Apply Online      Cal State LA on Twitter Cal State LA on Snapchat Cal State LA on Facebook Cal State LA on LinkedIn Cal State LA on Instagram        5151 State University Drive, Los Angeles, CA 90032 (323) 343-3000© 2019 Trustees of the California State University       File Viewers       '
    test_text = 'Office E&T 420 Phone (323) 343-669 Address 5151 State University Drive, Los Angeles, CA 90032 Web cs.calstatela.edu or www.calstatela.edu/cs'

    doc = nlp(test_text)
    #print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    plac.call(main)

