import React, {Component} from "react";
import URLPresenter from "./presenters/URLPresenter";
import StringsPresenter from "./presenters/StringsPresenter";
import LogPresenter from "./presenters/LogPresenter";

export default class AnalysisResults extends Component {
    getRefs(s) {
        let sHash = this.props.strings[s]
        return this.props.objects[sHash] && this.props.objects[sHash].refs;
    }

    hasRefs = (s) => {
        let refs = this.getRefs(s);
        return refs && refs.length;
    }

    showRefs = (s) => {
        let refs = this.getRefs(s);
        console.log(refs);
    }

    clearRefs = () => {

    }

    render() {
        return (
            <div class="analysis-results">
                <URLPresenter domains={this.props.domains}
                              hasRefs={this.hasRefs}
                              showRefs={this.showRefs}/>
                <StringsPresenter strings={Object.keys(this.props.strings)}
                                  hasRefs={this.hasRefs}
                                  showRefs={this.showRefs}/>
                <LogPresenter analysis={this.props.analysis}
                              logfiles={this.props.logfiles} />
            </div>
        )
    }
}
