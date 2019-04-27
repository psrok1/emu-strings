import React, {Component} from "react";
import { HashLink } from "react-router-hash-link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import axios from 'axios';
import { Hourglass } from "../Hourglass";
import AceEditor from "react-ace";

class SnippetViewer extends Component {
    state = {}

    componentDidMount() {
        this.updateSnippet();
    }

    componentDidUpdate(prevProps) {
        if(prevProps !== this.props)
            this.updateSnippet();
    }

    async updateSnippet() {
        this.setState({
            content: undefined
        })
        let aid = this.props.analysis;
        let snip = this.props.snippet;
        if(!snip)
            return;
        let response = await axios.get(`/api/analysis/${aid}/snippets/${snip}`);
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

export default class SnippetsPresenter extends Component {
    state = {}

    componentDidUpdate(prevProps) {
        if(prevProps !== this.props)
            this.setState({selected: undefined})
    }

    selectSnippet(snippet) {
        this.setState({selected: snippet})
    }

    render() {
        let snippets = this.props.snippets;
        return (
            <div>
                <h3 id="snippets">
                    <HashLink to="#snippets"><FontAwesomeIcon icon="link" /> Snippets</HashLink>
                </h3>
                <div>
                {
                    !Object.keys(snippets).length
                    ? (
                    <div class="alert alert-danger" role="alert">
                        No snippets found during analysis!
                    </div> )
                    : (
                        <div class="row">
                            <div class="col-3 nav nav-pills snippets">
                                {
                                    Object.keys(snippets)
                                          .sort((a,b) => snippets[b].size - snippets[a].size)
                                          .map(snippet => (
                                            <a className={`nav-link ${this.state.selected === snippet ? "active" : ""}`}
                                               href="#snippet"
                                               onClick={ev => { ev.preventDefault(); this.selectSnippet(snippet) }}>
                                                {snippet}
                                                <br/>
                                                Size: {snippets[snippet].size}
                                            </a>))
                                }
                            </div>
                            <div class="col">
                                {
                                    this.state.selected 
                                    ? <SnippetViewer 
                                        analysis={this.props.analysis}
                                        snippet={this.state.selected} />
                                    : <div className="snippet-view text-center">
                                        <FontAwesomeIcon icon="hand-point-left"/>
                                        <div>Select one of the snippets presented on the left</div>
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