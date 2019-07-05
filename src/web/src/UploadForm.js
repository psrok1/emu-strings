import React, { Component } from 'react';
import Dropzone from 'react-dropzone'
import axios from 'axios';

import { withRouter } from "react-router-dom";

class UploadForm extends Component {
    state = {
        language: "auto-detect",
        fileSelected: null,
        advancedCollapsed: false,
        softTimeout: 60,
        killAfterNext: 30,
    }
  
    handleFileChange = (acceptedFiles) => {
        let newState = {
            fileSelected: acceptedFiles[0]
        };
        let extension = newState.fileSelected.name.toLowerCase().split(".").pop();
        let language = ({
            "js": "JScript",
            "jse": "JScript.Encode",
            "vbs": "VBScript",
            "vbe": "VBScript.Encode"
        })[extension];
        if(language)
            newState["language"] = language;
        this.setState(newState);
    }

    getFieldHandler = (field) => {
        return (ev) => {
            let value = ev.target.value;
            this.setState({[field]: value});
        }
    }
    
    handleLanguageChange = (ev) => {
        let language = ev.target.value;
        this.setState({language});
    }

    handleSoftTimeoutChange = (ev) => {
        let softTimeout = ev.target.value;
        this.setState({softTimeout});
    }

    handleKillAfterNextChange = (ev) => {
        let killAfterNext = ev.target.value;
        this.setState({killAfterNext});
    }

    handleSubmit = (ev) => {
        ev.preventDefault();
        let form = new FormData();
        form.set('file', this.state.fileSelected)
        form.set('options', JSON.stringify({
            soft_timeout: Math.max(15, Math.min(600, this.state.softTimeout)),
            hard_timeout: Math.max(15, Math.min(600, this.state.killAfterNext)) + this.state.softTimeout,
            language: this.state.language
        }))
        axios.post("/api/submit", form)
             .then(response => {
                 this.props.history.push(`/analysis/${response.data.aid}`);
             })
    }

    toggleAdvancedCollapse = (ev) => {
        ev.preventDefault();
        this.setState({advancedCollapsed: !this.state.advancedCollapsed});
    }
  
    render() {
        return (
            <form class="mid-width text-center" onSubmit={this.handleSubmit}>
                <Dropzone className="dropzone" 
                        multiple={false} 
                        name="file"
                        onDrop={this.handleFileChange}>
                {this.state.fileSelected ? this.state.fileSelected.name : "Click to select file to upload"}
                </Dropzone>
                <div class="card">
                    <div class="card-header">
                        Analysis options
                    </div>
                    <div class="card-body">
                        <div class="form-group row text-left">
                            <label for="language" class="col-sm-3 col-form-label">Script language</label>
                            <div class="col-sm-9">
                                <select className="form-control custom-select" 
                                        name="language" 
                                        value={this.state.language} 
                                        onChange={this.handleLanguageChange}>
                                    <option key="auto-detect">(auto-detect)</option>
                                    <option key="JScript">JScript</option>
                                    <option key="JScript.Encode">JScript.Encode</option>
                                    <option key="VBScript">VBScript</option>
                                    <option key="VBScript.Encode">VBScript.Encode</option>
                                </select>
                            </div>
                        </div>
                        <a data-toggle="collapse"
                           href="#advancedOptions"
                           onClick={this.toggleAdvancedCollapse}>
                            <b>Advanced options</b>
                        </a>
                        <div id="advancedOptions" className={`collapse ${this.state.advancedCollapsed ? "show" : ""}`}>
                            <div class="form-group row text-left">
                                <label for="soft-timeout" class="col-sm-3 col-form-label">Analysis timeout</label>
                                <div class="col-sm-9">
                                    <input className="form-control"
                                           name="soft-timeout"
                                           type="number"
                                           value={this.state.softTimeout}
                                           onChange={this.handleSoftTimeoutChange}/>
                                </div>
                            </div>
                            <div class="form-group row text-left">
                                <label for="kill-after-next" class="col-sm-3 col-form-label">Kill after next</label>
                                <div class="col-sm-9">
                                    <input className="form-control"
                                           name="kill-after-next"
                                           type="number"
                                           value={this.state.killAfterNext}
                                           onChange={this.handleKillAfterNextChange}/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <button class="btn btn-lg btn-primary btn-block" type="submit" disabled={!this.state.fileSelected}>Analyze!</button>
            </form>
        );
    }
}

export default withRouter(UploadForm);
