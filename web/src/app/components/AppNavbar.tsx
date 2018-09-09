import * as React from 'react';
import { Link } from 'react-router-dom';
import { Nav, Navbar, NavItem } from "react-bootstrap";

export class AppNavbar extends React.Component<{}, {}> {
    render() {
        return (
            <Navbar inverse collapseOnSelect>
                <Navbar.Header>
                <Navbar.Brand>
                    <Link to="/">Winedrop</Link>
                </Navbar.Brand>
                <Navbar.Toggle />
                </Navbar.Header>
                <Navbar.Collapse>
                <Nav>
                    <NavItem eventKey={1} href="#">
                        <Link to="/submit">Submit file</Link>
                    </NavItem>
                    <NavItem eventKey={2} href="#">
                        <Link to="/about">About</Link>
                    </NavItem>
                </Nav>
                </Navbar.Collapse>
            </Navbar>
        );
    }
}

