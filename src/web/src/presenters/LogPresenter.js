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
        let emulator = this.props.emulator;
        let logid = this.props.log;
        if(!emulator || !logid)
            return;
        let response = await axios.get(`/api/analysis/${aid}/logfile/${emulator}/${logid}`);
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
            this.setState({
                emulator: undefined,
                selected: undefined
            })
    }

    selectLog(logfile) {
        this.setState({selected: logfile})
    }

    switchEmulator(emulator) {
        this.setState({emulator, selected: undefined})
    }

    render() {
        let logfiles = this.props.logfiles;
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
                    <div>
                        <ul className="nav nav-tabs">
                            {
                                Object.keys(logfiles).map(emulator => (
                                    <li className="nav-item">
                                        <a className={`nav-link ${this.state.emulator === emulator ? "active" : ""}`}
                                            href="#emulator"
                                            onClick={ev => {ev.preventDefault(); this.switchEmulator(emulator)}}>
                                            {emulator}
                                        </a>
                                    </li>
                                ))
                            }
                        </ul>
                        {
                            this.state.emulator ?
                            <div class="row">
                                <div class="col-3 nav nav-pills snippets">
                                    {
                                        logfiles[this.state.emulator].map(log => {
                                            return <a className={`nav-link ${this.state.selected === log ? "active" : ""}`}
                                                    href="#logfile"
                                                    onClick={ev => { ev.preventDefault(); this.selectLog(log) }}>
                                                        {log}
                                            </a>
                                        })
                                    }
                                </div>
                                <div class="col">
                                    {
                                        this.state.selected 
                                        ? <LogViewer 
                                            analysis={this.props.analysis}
                                            emulator={this.state.emulator}
                                            log={this.state.selected} />
                                        : <div className="snippet-view text-center">
                                            <FontAwesomeIcon icon="hand-point-left"/>
                                            <div>Select one of the analysis logs presented on the left</div>
                                        </div>
                                    }
                                </div>
                            </div>
                            : []
                        }
                    </div>
                    )
                }
                </div>
            </div>
        )
    }
}