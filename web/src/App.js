import React, { Component } from 'react';
import { BrowserRouter, Link } from 'react-router-dom';
import { Switch, Route } from 'react-router';

import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import logo from "./logo.jpg";
import UploadForm from './UploadForm';
import AnalysisView from './AnalysisView';

class App extends Component {
  render() {
    return (
      <BrowserRouter>
        <div class="text-center">
          <Link to="/">
            <img src={logo} alt="logo" width="700px" class="logo"/>
          </Link>
          <Switch>
            <Route exact path='/' component={UploadForm}/>
            <Route exact path='/analysis/:aid' component={AnalysisView}/>
          </Switch>
        </div>
      </BrowserRouter>
    );
  }
}

export default App;
