import React from 'react';

import styled from 'styled-components';

const Navbar = styled.div`
    background: #bbbbbb55;
    padding: 10px;
    margin-bottom: 30px;
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-rows: 1fr;
    justify-items: end;
`;

const NavbarComponent = ({ round }) => <Navbar>Round: {round}</Navbar>;

export default NavbarComponent;
