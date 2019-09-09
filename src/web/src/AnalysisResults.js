import React, {Component} from "react";
import URLPresenter from "./presenters/URLPresenter";
import StringsPresenter from "./presenters/StringsPresenter";
import SnippetsPresenter from "./presenters/SnippetsPresenter";
import LogPresenter from "./presenters/LogPresenter";

export default class AnalysisResults extends Component {
    state = { filterRefs: null }

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
        this.setState({referee: s, filterRefs: refs})
    }

    clearRefs = () => {
        this.setState({filterRefs: null})
    }

    get snippets()
    {
        let shorts = Object.values(this.props.strings);
        return Object.keys(this.props.objects)
                     .filter(key => !shorts.includes(key))
                     .reduce((obj, key) => (
                         {
                            ...obj,
                            [key]: (this.props.objects[key])
                         }
                     ), {});
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
                <SnippetsPresenter analysis={this.props.analysis}
                                   snippets={this.snippets}
                                   refs={this.state.filterRefs}
                                   referee={this.state.referee}
                                   clearRefs={this.clearRefs}/>
                <LogPresenter analysis={this.props.analysis}
                              logfiles={this.props.logfiles} />
            </div>
        )
    }
}
