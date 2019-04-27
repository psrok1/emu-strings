import React, { Component } from 'react';
import axios from 'axios';

import { Hourglass, brokenglass } from "./Hourglass";
import AnalysisStatus, * as status from "./AnalysisStatus";
import AnalysisResults from './AnalysisResults';

class AnalysisView extends Component {
    state = {}

    scheduleRefresh() {
        this.timer = setTimeout(this.updateAnalysis, 2000);
    }

    componentWillUnmount()
    {
        if(this.timer)
            clearTimeout(this.timer);
    }

    componentDidMount() {
        this.updateAnalysis()
    }

    componentDidUpdate(prevProps) {
        if (prevProps !== this.props)
            this.updateAnalysis();
    };

    updateAnalysis = async () => {
        let response = await axios.get(`/api/analysis/${this.props.match.params.aid}`);
        let analysis = response.data;
        this.setState({analysis});
        if(analysis.status === status.STATUS_PENDING ||
           analysis.status === status.STATUS_IN_PROGRESS) {
            this.scheduleRefresh();
        }
    }

    render() {
        if(!this.state.analysis) {
            return <Hourglass/>
        } else if (!this.state.analysis.sample) {
            return <Hourglass hourglass={brokenglass} message="Analysis not found"/>
        }
        return (
        <div className="justify-content-center">
            <div className="card">
                <div className="card-header">
                    <strong>Analysis details</strong>
                </div>
                <div className="card-body">
                    <p>
                        <table className="table table-borderless">
                            <tr>
                                <th>File name:</th>
                                <td>{this.state.analysis.sample.name}</td>
                            </tr>
                            <tr>
                                <th>SHA256:</th>
                                <td>{this.state.analysis.sample.sha256}</td>
                            </tr>
                            <tr>
                                <th>MD5:</th>
                                <td>{this.state.analysis.sample.md5}</td>
                            </tr>
                            <tr>
                                <th>Language:</th>
                                <td>{this.state.analysis.language}</td>
                            </tr>
                            <tr>
                                <th>Analysis status:</th>
                                <td><AnalysisStatus status={this.state.analysis.status}/></td>
                            </tr>
                        </table>
                    </p>
                </div>
            </div>
            {
                this.state.analysis.error ?
                    <pre className="exception alert-danger">{this.state.analysis.error}</pre>
                    : []
            }
            {
                this.state.analysis.status === status.STATUS_SUCCESS ?
                    <AnalysisResults {...this.state.analysis.results} 
                                     analysis={this.props.match.params.aid}/>
                    : []
            }
        </div>)
        /*
        if(this.state.error)
            return <Hourglass hourglass={brokenglass} message={this.state.error} />
        return <Hourglass message={this.state.status || "Checking analysis status..."} />
        */
    }
}

export default AnalysisView;
