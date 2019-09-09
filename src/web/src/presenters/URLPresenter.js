import React, {Component} from "react";
import { HashLink } from "react-router-hash-link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { StringsViewer } from "./StringsPresenter";

class URLViewer extends Component {
    state = { shownDomains: {} }

    toggleCollapse = (domain) => {
        this.setState({
            shownDomains: {
                ...this.state.shownDomains,
                [domain]: !this.state.shownDomains[domain]
            }
        });
    }
    
    render() {
        if(this.props.raw)
        {
            let strings = [].concat(...Object.values(this.props.domains)).sort();
            return <StringsViewer strings={strings}
                                  hasRefs={this.props.hasRefs}
                                  showRefs={this.props.showRefs}/>
        }
        let domains = this.props.domains;
        return <div>
            {
                Object.keys(domains).sort().map(domain => (
                    <div className="card">
                        <div className="card-header">
                            <span className="badge badge-primary">{domains[domain].length}</span>
                            <button className="btn btn-link"
                                    onClick={ev => { ev.preventDefault(); this.toggleCollapse(domain); }}>
                                {domain}
                            </button>
                        </div>
                        <div className={`collapse ${this.state.shownDomains[domain] ? "show" : ""}`}>
                            <StringsViewer strings={domains[domain].sort()}
                                           hasRefs={this.props.hasRefs}
                                           showRefs={this.props.showRefs}/>
                        </div>
                    </div>
                ))
            }
        </div>
    }
}

export default class URLPresenter extends Component {
    state = {}

    switchView(enableRaw) {
        this.setState({raw: enableRaw})
    }

    render() {
        return (
            <div>
                <h3 id="URLs">
                    <HashLink to="#URLs"><FontAwesomeIcon icon="link" /> URLs</HashLink>
                </h3>
                {
                    !Object.keys(this.props.domains).length
                    ? (
                    <div class="alert alert-danger" role="alert">
                        No URLs found during analysis!
                    </div> )
                    : (
                        <div>
                            <ul className="nav nav-tabs">
                                <li className="nav-item">
                                    <a className={`nav-link ${!this.state.raw ? "active" : ""}`}
                                       href="#url-detailed"
                                       onClick={ev => {ev.preventDefault(); this.switchView(false)}}>
                                       Aggregated view
                                    </a>
                                </li>
                                <li className="nav-item">
                                    <a className={`nav-link ${this.state.raw ? "active" : ""}`}
                                       href="#url-raw"
                                       onClick={ev => {ev.preventDefault(); this.switchView(true)}}>
                                       Plain view
                                    </a>
                                </li>
                            </ul>
                            <URLViewer domains={this.props.domains}
                                       raw={this.state.raw}
                                       showRefs={this.props.showRefs}
                                       hasRefs={this.props.hasRefs}/>
                        </div>
                    )
                }
            </div>
        )
    }
}