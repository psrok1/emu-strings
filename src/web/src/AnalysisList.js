import React, { Component } from 'react';
import {Link} from 'react-router-dom';
import axios from 'axios';
import Pagination from './Pagination';
import { Hourglass } from './Hourglass';
import AnalysisStatus from './AnalysisStatus';

export default class AnalysisList extends Component {
    entriesPerPage = 7

    state = {
        page: -1,
        analyses: [],
        loading: true
    }

    async loadList(lastId) {
        lastId = lastId || "";
        let response = await axios.get(`/api/analysis`, {
            params: { lastId }
        })
        return response.data
    }

    get hasMoreElements() {
        let currentPage = this.state.analyses[this.state.page] || []
        let nextPage = this.state.analyses[this.state.page+1] || []
        return currentPage.length === this.entriesPerPage && nextPage.length > 0
    }

    async componentDidMount() {
        this.loadNextPage();
    }

    async loadNextPage() {
        this.setState({loading: true})
        let pageNo = this.state.page + 1;
        let page = this.state.analyses[pageNo] || [];
        // If first page - fetch
        if(!pageNo)
        {
            page = await this.loadList();
            this.setState({analyses: this.state.analyses.concat([page])});
        }
        this.setState({
            page: pageNo
        })
        // Prefetch next pages
        if(page.length === this.entriesPerPage)
        {
            let nextPage = await this.loadList((page.slice(-1).pop() || {})["_id"])
            this.setState({
                analyses: this.state.analyses.concat([nextPage])
            });
        }
        this.setState({
            loading: false            
        })
    }
    
    render() {
        return (
            <div>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Sample</th>
                            <th>Language</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            this.state.page >= 0 ?
                                (!(this.state.analyses[this.state.page] || []).length
                                    ? <tr>
                                        <td colspan="4" className="text-center">
                                            (No entries found) <br/>
                                            <Link to="/submit">
                                            Submit first sample!
                                            </Link>
                                        </td>
                                    </tr>
                                    : this.state.analyses[this.state.page].map(entry => (
                                        <tr>
                                            <td className="cell-ellipsis">
                                                <Link to={`/analysis/${entry.aid}`}>
                                                    {entry.aid}
                                                </Link>
                                                <br/>
                                                {entry.timestamp}
                                            </td>
                                            <td className="cell-ellipsis">
                                                <b>File name:</b> {entry.sample.name}
                                                <br/>
                                                <b>SHA256:</b> {entry.sample.sha256}
                                            </td>
                                            <td>{entry.sample.language}</td>
                                            <td><AnalysisStatus status={entry.status}/></td>
                                        </tr>
                                )))
                                : <tr> 
                                    <td colspan="4"><Hourglass/></td>
                                  </tr>
                        }
                    </tbody>
                </table>
                <Pagination 
                    disabled={this.state.loading}
                    page={this.state.page + 1}
                    hasMore={this.hasMoreElements}
                    previous={() => this.setState({page: this.state.page - 1})}
                    next={() => this.loadNextPage()}
                />
            </div>
        )
    }
}