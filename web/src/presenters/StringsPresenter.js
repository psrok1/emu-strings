import React, {Component} from "react";
import { HashLink } from "react-router-hash-link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

export default class StringsPresenter extends Component {
    state = {
        sortMode: "alpha"
    }

    sortFn = {
        alpha: ((a, b) => a.toLowerCase() > b.toLowerCase()),
        alphaReversed: ((a, b) => a.toLowerCase() < b.toLowerCase()),
        length: ((a, b) => a.length > b.length),
        lengthReversed: ((a, b) => a.length < b.length),
    }

    toggleSortAlphabetically() {
        this.setState({
            sortMode: this.state.sortMode === "alpha" ? "alphaReversed" : "alpha"
        })
    }

    toggleSortByLength() {
        this.setState({
            sortMode: this.state.sortMode === "length" ? "lengthReversed" : "length"
        })
    }

    get sortedStrings() {
        return this.props.strings.sort(this.sortFn[this.state.sortMode]);
    }

    render() {
        return (
            <div>
                <h3 id="strings">
                    <HashLink to="#strings"><FontAwesomeIcon icon="link" /> Strings</HashLink>
                </h3>
                {
                    !this.props.strings.length
                    ? (
                    <div class="alert alert-danger" role="alert">
                        No strings found during analysis!
                    </div> )
                    : (
                        <div>
                            <ul className="nav nav-pills">
                                <li className="nav-item">
                                    <a className={`nav-link ${this.state.sortMode.startsWith("alpha") ? "active" : ""}`}
                                       href="#sort-alpha"
                                       onClick={ev => {ev.preventDefault(); this.toggleSortAlphabetically(); }}>
                                        <FontAwesomeIcon icon={
                                            this.state.sortMode === "alphaReversed" ? "sort-alpha-up" : "sort-alpha-down"
                                        }/> Sort alphabetically
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a className={`nav-link ${this.state.sortMode.startsWith("length") ? "active" : ""}`}
                                       href="#sort-alpha"
                                       onClick={ev => {ev.preventDefault(); this.toggleSortByLength(); }}>
                                        <FontAwesomeIcon icon={
                                            this.state.sortMode === "lengthReversed" ? "sort-amount-up" : "sort-amount-down"
                                        }/> Sort by length
                                    </a>
                                </li>
                            </ul>
                            <pre className="strings">{this.sortedStrings.join('\n')}</pre>
                        </div>
                    )
                }
            </div>
        )
    }
}