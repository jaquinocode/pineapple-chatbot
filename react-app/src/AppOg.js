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
        <Title />
        <MessageList messages={this.state.messages} />
        <SendMessageForm sendMessage={this.sendMessage} />
      </div>
    );
  }
}

class MessageList extends React.Component {
  render() {
    return (
      <ul className="message-list">
        {this.props.messages.map(message => {
          return (
            <li key={message.id} className="message">
              <div>{message.senderId}</div>
              <div>
                <a target="_blank" href={message.text}>
                  {message.text}
                </a>
              </div>
            </li>
          );
        })}
      </ul>
    );
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

export default App;
