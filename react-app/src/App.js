import React, { Component } from "react";
import "./style.css";

import axios from "axios";

class App extends Component {
  constructor() {
    super();
    this.state = {
      messages: []
    };
    this.sendMessage = this.sendMessage.bind(this);
  }

  sendMessage(text, sender) {
    this.messageToSend = {
      senderId: sender,
      text: text
    };

    this.setState({
      messages: [...this.state.messages, this.messageToSend]
    });
  }

  render() {
    return (
      <div className="app">
     	<SideLeft />
     	<div class = "split right">
         <Title />
			   <div className="messageListContainer">
		        <MessageList messages={this.state.messages} />
            <SendMessageForm sendMessage={this.sendMessage} />
		  	 </div>
	    </div>        
      </div>
    );
  }
}

class MessageList extends React.Component {
  render() {
    return (
	  <ul className="message-list">
       <li >
          <div className="bot-id">pineapple</div>
          <div className="bot-message">Hello! What can I help you with?</div>
        </li>
	    {this.props.messages.map(message => {
        if (message.senderId === "pineapple") {
          if (message.text[0] === "$") {
            return (
              <li key={message.id} >
                <div className="bot-id">{message.senderId}</div>
                <div className="bot-message">{message.text.slice(1, message.text.indexOf(':') + 1)}</div>
                  {message.text.slice(message.text.indexOf(':') + 3, -1).split(", ").map((e, index) => {
                    console.log(e)
                    return (
                      <div key={index} >
                        <br/>
                        <a className="links" href={e.slice(1,-1)} target="_blank">{e.slice(1,-1)}</a>
                      </div>
                    );
                  })}
              </li>
            );  
          }
          else if (message.text[0] === "#") {
            return (
              <li key={message.id} >
                <div className="bot-id">{message.senderId}</div>
                <div className="bot-message">{message.text.slice(1, message.text.indexOf("^"))}</div>
                  <div>
                    <br/>
                    <a className="links" href={message.text.slice(message.text.indexOf("^")+1)} target="_blank">{message.text.slice(message.text.indexOf("^")+1)}</a>
                  </div>
              </li>
            );  
          }
          else {
            return (
              <li key={message.id}>
                <div className="bot-id">{message.senderId}</div>
                <div className="bot-message">{message.text}</div>
              </li>
            );  
          }          
        }
        else {
          return (
            <li key={message.id} className="user-message">
              <div>{message.senderId}</div>
              <div align="right"><p className="message-text">{message.text}</p></div>
            </li>
          );
        }
     })}
     <div style={{ float:"left", clear: "both" }}
             ref={(el) => { this.messagesEnd = el; }}>
      </div>
	  </ul>
    );
  }

  scrollToBottom = () => {
    this.messagesEnd.scrollIntoView({ behavior: "smooth" });
  }
  
  componentDidMount() {
    this.scrollToBottom();
  }
  
  componentDidUpdate() {
    this.scrollToBottom();
  }
}

class SendMessageForm extends React.Component {
  constructor() {
    super();
    this.state = {
      message: ""
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(e) {
    this.setState({
      message: e.target.value
    });
  }

  handleSubmit(e) {
    e.preventDefault();

    if (this.state.message != '') {
      this.props.sendMessage(this.state.message, "user");

      axios
        .post("/statement", {
          input: this.state.message
        })
        .then(response => {
          console.log(response);
          this.props.sendMessage(response.data, "pineapple");
        })
        .catch(function(error) {
          console.log(error);
        });
  
      this.setState({
        message: ""
      });
    } 
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="send-message-form">
        <input
          onChange={this.handleChange}
          value={this.state.message}
          placeholder="Type your message and hit ENTER"
          type="text"
        />
      </form>
    );
  }
}

function Title() {
  return <p className="title">Pineapple Chatbot</p>;
}

function SideLeft() {
	return (
		<div class = "split left">
        <div class = "centered">
            <img class = "logo" src = "https://upload.wikimedia.org/wikipedia/en/f/f7/CSU%2C_Los_Angeles_seal.svg" alt ="Cal state la logo" />
            <h2>Pineapple ChatBot</h2>
        	</div>
    	</div>
     );
}

export default App;
