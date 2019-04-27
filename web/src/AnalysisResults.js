import React, {Component} from "react";
import URLPresenter from "./presenters/URLPresenter";
import StringsPresenter from "./presenters/StringsPresenter";
import SnippetsPresenter from "./presenters/SnippetsPresenter";
import LogPresenter from "./presenters/LogPresenter";

export default class AnalysisResults extends Component {
    render() {
        return (
            <div class="analysis-results">
                <URLPresenter {...this.props}/>
                <StringsPresenter {...this.props}/>
                <SnippetsPresenter {...this.props} analysis={this.props.analysis} />
                <LogPresenter {...this.props} analysis={this.props.analysis} />
            </div>
        )
    }
}
