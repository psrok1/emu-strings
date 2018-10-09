import React, { Component } from 'react';
import axios from 'axios';

import hourglass from "./hourglass.gif";
import brokenglass from "./brokenglass.png";

function Hourglass(props) {
    return (
      <div class="hourglass">
        <img src={props.hourglass || hourglass} alt="hourglass" width="200px"/>
        <h3>{props.message}</h3>
      </div>
    )
}
  
function Strings(props) {
    return (
      <div class="results">
        <pre class="strings">
          {props.children}
        </pre>
      </div>
    )
}

class AnalysisView extends Component {
    state = {}

    scheduleRefresh() {
        this.timer = setTimeout(
            this.updateAnalysis.bind(this),
            2000);
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

    updateAnalysis() {
        const STATUS_PENDING = 0;
        const STATUS_IN_PROGRESS = 1;
        const STATUS_SUCCESS = 2;
        const STATUS_FAILED = 3;
        axios.get(`/api/analysis/${this.props.match.params.aid}`)
             .then(response => {
                 let analysis = response.data;
                 if(!analysis.status)
                 {
                     this.setState({"error": "Analysis not found"})
                 }
                 else if(analysis.status === STATUS_PENDING)
                 {
                     this.setState({"status": "Waiting for analysis to start..."})
                     this.scheduleRefresh();
                 }
                 else if(analysis.status === STATUS_IN_PROGRESS)
                 {
                     this.setState({"status": "Sample analysis in progress..."})
                     this.scheduleRefresh();
                 }
                 else if(analysis.status === STATUS_SUCCESS)
                 {
                     this.setState({"strings": analysis.strings})
                 }
                 else if(analysis.status === STATUS_FAILED)
                 {
                     this.setState({"error": "Analysis failed"})
                 }
             })
    }

    render() {
        if(this.state.error)
            return <Hourglass hourglass={brokenglass} message={this.state.error} />
        if(this.state.strings)
            return <Strings>{this.state.strings}</Strings>
        return <Hourglass message={this.state.status || "Checking analysis status..."} />
    }
}

export default AnalysisView;
