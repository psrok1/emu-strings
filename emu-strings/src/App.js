import React, { Component } from 'react';
import Dropzone from 'react-dropzone'

import './App.css';
import "../node_modules/bootstrap/dist/css/bootstrap.min.css"
import logo from "./logo.jpg";

class App extends Component {
  state = {
    engine: "JScript",
    fileSelected: null
  }

  render() {
    return (
      <div class="text-center">
        <img src={logo} alt="logo" width="700px"/>
        <form class="form-submit">
          <h1 class="h3 mb-3 font-weight-normal">Analyze malware</h1>
          <Dropzone className="dropzone" 
                    multiple={false} 
                    name="file"
                    onDrop={(acceptedFiles) => {
                      let newState = {
                        fileSelected: acceptedFiles[0].name
                      };
                      let engine = ({
                        "js": "JScript",
                        "jse": "JScript.Encode",
                        "vbs": "VBScript",
                        "vbe": "VBScript.Encode"
                      })[newState.fileSelected.toLowerCase().split(".").pop()];
                      if(engine)
                        newState["engine"] = engine;
                      this.setState(newState);
                    }}>
            {this.state.fileSelected || "Click to select file to upload"}
          </Dropzone>
          <div class="form-group">
            <label for="engineSelect">Choose engine</label>
            <select class="form-control" id="engineSelect" name="engine" value={this.state.engine}>
              <option key="JScript">JScript</option>
              <option key="JScript.Encode">JScript.Encode</option>
              <option key="VBScript">VBScript</option>
              <option key="VBScript.Encode">VBScript.Encode</option>
            </select>
          </div>
          <button class="btn btn-lg btn-primary btn-block" type="submit" disabled={!this.state.fileSelected}>Submit!</button>
          <p class="mt-5 mb-3 text-muted">psrok1 @ 2018</p>
        </form>
      </div>
    );
  }
}

export default App;
