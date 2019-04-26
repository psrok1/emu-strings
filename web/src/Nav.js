import React, { Component } from 'react';
import { Link } from "react-router-dom";

import logo from "./logo_short.gif";

export default class Nav extends Component{
    render() {
        return (
            <nav className="navbar navbar-expand-md navbar-dark bg-dark">
                <div className="container">
                    <Link className="navbar-brand" to="/">
                        <img src={logo} style={
                            {
                                height: "3rem", 
                                marginRight: "1rem"
                            }}/>
                        emu-strings
                    </Link>
                    <div className="collapse navbar-collapse" id="navbarsExampleDefault">
                        <ul className="navbar-nav mr-auto">
                            <li className="nav-item">
                                <Link to="/submit" className="nav-link">Submit file...</Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        );
    }
}