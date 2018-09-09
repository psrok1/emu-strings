import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { BrowserRouter, Route } from "react-router-dom";

import { AppNavbar } from "./components/AppNavbar";

import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';

import { Hello } from './components/Hello';

ReactDOM.render(
    <div>
        <AppNavbar/>
        <BrowserRouter>
            <Route path='/' component={Hello}/>
        </BrowserRouter>
    </div>,
    document.getElementById('root'));