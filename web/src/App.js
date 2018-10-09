import React, { Component } from 'react';
import './App.css';
import "../node_modules/bootstrap/dist/css/bootstrap.min.css"
import logo from "./logo.jpg";
import UploadForm from './UploadForm';

class App extends Component {
  state = {
    engine: "JScript",
    fileSelected: null
  }

  render() {
    return (
      <div class="text-center">
        <img src={logo} alt="logo" width="700px"/>
        <UploadForm />
      </div>
    );
  }
}

export default App;
