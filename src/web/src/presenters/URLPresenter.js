import React, {Component} from "react";
import { HashLink } from "react-router-hash-link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

class URLViewer extends Component {
    state = { shownDomains: {} }

    getOriginWeight(originSet) {
        /**
         * URL sorting rules (first group is considered "most reliable"):
         * - URLs that dropper connected with
         * - URLs found in strings
         * - URLs found in snippets
         */
        if(originSet.indexOf("connection") > -1)
            return 2;
        else if(originSet.indexOf("string") > -1)
            return 1;
        return 0;
    }

    aggregatedData() {
        let result = {};
        let domains = this.props.urls;
        let origins = this.props.urlOrigins;
        for(let domain in domains) {
            result[domain] = {
                urls: [],
                weight: 0,
                snippets: []
            }
            for(let url of domains[domain]) {
                let snippets = origins[url].filter(v => Array.isArray(v) && v[0] === "snippet").map(v => v[1]);
                let weight = this.getOriginWeight(origins[url]);
                result[domain].urls.push(
                    {
                        url,
                        weight: weight,
                        origin: origins[url]
                    })
                result[domain].weight = Math.max(result[domain].weight, weight)
                result[domain].snippets = result[domain].snippets.concat(snippets)
            }
        }
        return result;
    }

    toggleCollapse = (domain) => {
        this.setState({
            shownDomains: {
                ...this.state.shownDomains,
                [domain]: !this.state.shownDomains[domain]
            }
        });
    }

    render() {
        let data = this.aggregatedData()
        if(this.props.raw) {
            /**
             * Raw view
             */
            let raw = [].concat(...Object.keys(data)
                              .sort((a, b) => b.weight - a.weight)
                              .map(domain => data[domain].urls)
                              .map(urls => urls.sort((a, b) => b.weight - a.weight)
                                               .map(url => url.url)))
            return <pre className="strings">{raw.join('\n')}</pre>
        }
        /**
         * Detailed view
         */
        return (
        <div>
            {
                Object.keys(data).sort((a, b) => b.weight - a.weight).map(domain => (
                    <div className="card">
                        <div className={`card-header ${domain.weight > 1 ? "alert-warning" : ""}`}>
                            <span className="badge badge-primary">{data[domain].urls.length}</span>
                            <button className="btn btn-link"
                                    onClick={ev => { ev.preventDefault(); this.toggleCollapse(domain); }}>
                                {domain}
                            </button>
                        </div>
                        <div className={`collapse ${this.state.shownDomains[domain] ? "show" : ""}`}>
                            <table className="table">
                            {
                                data[domain].urls.sort((a, b) => b.weight - a.weight).map(url => (
                                    <tr className={domain.weight > 1 && "table-warning"}>
                                        <td>
                                            {url.url}
                                        </td>
                                    </tr>
                                ))
                            }
                            </table>
                        </div>
                    </div>
                ))
            }
        </div>
        )
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
                    !Object.keys(this.props.urls).length
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
                                       Detailed view
                                    </a>
                                </li>
                                <li className="nav-item">
                                    <a className={`nav-link ${this.state.raw ? "active" : ""}`}
                                       href="#url-raw"
                                       onClick={ev => {ev.preventDefault(); this.switchView(true)}}>
                                       Raw view
                                    </a>
                                </li>
                            </ul>
                            <URLViewer urls={this.props.urls} urlOrigins={this.props.url_origins}
                                       raw={this.state.raw}/>
                        </div>
                    )
                }
            </div>
        )
    }
}