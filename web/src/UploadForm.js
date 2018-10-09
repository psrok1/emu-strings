import React, { Component } from 'react';
import Dropzone from 'react-dropzone'
import axios from 'axios';

import { withRouter } from "react-router-dom";



class UploadForm extends Component {
    state = {
        engine: "JScript",
        fileSelected: null
    }
  
    handleFileChange(acceptedFiles) {
        let newState = {
            fileSelected: acceptedFiles[0]
        };
        let engine = ({
            "js": "JScript",
            "jse": "JScript.Encode",
            "vbs": "VBScript",
            "vbe": "VBScript.Encode"
        })[newState.fileSelected.name.toLowerCase().split(".").pop()];
        if(engine)
            newState["engine"] = engine;
        this.setState(newState);
    }

    handleEngineChange(ev) {
        let engine = ev.target.value;
        this.setState({"engine": engine});
    }

    handleSubmit(ev) {
        ev.preventDefault();
        let form = new FormData();
        form.set('engine', this.state.engine)
        form.set('file', this.state.fileSelected)
        axios.post("/api/submit", form)
             .then(response => {
                 this.props.history.push(`/analysis/${response.data.aid}`);
             })
    }
  
    render() {
        return (
            <form class="form-submit" onSubmit={this.handleSubmit.bind(this)}>
                <Dropzone className="dropzone" 
                          multiple={false} 
                          name="file"
                          onDrop={this.handleFileChange.bind(this)}>
                {this.state.fileSelected ? this.state.fileSelected.name : "Click to select file to upload"}
                </Dropzone>
                <div class="form-group">
                    <label for="engineSelect">Choose engine</label>
                    <select class="form-control" id="engineSelect" name="engine" value={this.state.engine} onChange={this.handleEngineChange.bind(this)}>
                        <option key="JScript">JScript</option>
                        <option key="JScript.Encode">JScript.Encode</option>
                        <option key="VBScript">VBScript</option>
                        <option key="VBScript.Encode">VBScript.Encode</option>
                    </select>
                </div>
                <button class="btn btn-lg btn-primary btn-block" type="submit" disabled={!this.state.fileSelected}>Submit!</button>
                <p class="mt-5 mb-3 text-muted">psrok1 @ 2018</p>
            </form>
        );
    }
}

export default withRouter(UploadForm);
