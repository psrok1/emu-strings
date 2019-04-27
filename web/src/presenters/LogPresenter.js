import React, {Component} from "react";
import { HashLink } from "react-router-hash-link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import axios from 'axios';
import { Hourglass } from "../Hourglass";
import AceEditor from "react-ace";

class LogViewer extends Component {
    state = {}

    componentDidMount() {
        this.updateLog();
    }

    componentDidUpdate(prevProps) {
        if(prevProps !== this.props)
            this.updateLog();
    }

    async updateLog() {
        this.setState({
            content: undefined
        })
        let aid = this.props.analysis;
        let logid = this.props.log;
        if(!logid)
            return;
        let response = await axios.get(`/api/analysis/${aid}/logfiles/${logid}`);
        this.setState({
            content: response.data
        })
    }

    render() {
        if(!this.state.content)
            return <Hourglass />
        return <AceEditor value={this.state.content}
                          className="snippet-view"
                          fontSize={14}
                          readOnly
                          showGutter
                          wrapEnabled />
    }
}

export default class LogPresenter extends Component {
    state = {}

    componentDidUpdate(prevProps) {
        if(prevProps !== this.props)
            this.setState({selected: undefined})
    }

    selectLog(logfile) {
        this.setState({selected: logfile})
    }

    render() {
        let logfiles = this.props.logfiles;
        let logs = [].concat(...Object.keys(logfiles)
                                      .map(emulator => Object.keys(logfiles[emulator])
                                                             .map(identifier => ({emulator, identifier}))))
        return (
            <div>
                <h3 id="logs">
                    <HashLink to="#logs"><FontAwesomeIcon icon="link" /> Analysis logs</HashLink>
                </h3>
                <div>
                {
                    !Object.keys(logfiles).length
                    ? (
                    <div class="alert alert-danger" role="alert">
                        No logs created during analysis!
                    </div> )
                    : (
                        <div class="row">
                            <div class="col-3 nav nav-pills snippets">
                                {
                                    logs.map(log => {
                                        let logid = `${log.emulator}-${log.identifier}`;
                                        return <a className={`nav-link ${this.state.selected === logid ? "active" : ""}`}
                                                  href="#logfile"
                                                  onClick={ev => { ev.preventDefault(); this.selectLog(logid) }}>
                                                    {log.identifier}
                                                    <br/>
                                                    Emulator {log.emulator}
                                        </a>
                                    })
                                }
                            </div>
                            <div class="col">
                                {
                                    this.state.selected 
                                    ? <LogViewer 
                                        analysis={this.props.analysis}
                                        log={this.state.selected} />
                                    : <div className="snippet-view text-center">
                                        <FontAwesomeIcon icon="hand-point-left"/>
                                        <div>Select one of the analysis logs presented on the left</div>
                                    </div>
                                }
                            </div>
                        </div>
                    )
                }
                </div>
            </div>
        )
    }
}