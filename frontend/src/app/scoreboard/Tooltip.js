import React from 'react';

import styled from 'styled-components';

const Tooltip = styled.div`
    background-color: #333333;
    color: #f3f3f3;
    position: absolute;
    width: 100%;
    height: 100%;
    display: grid;
    align-content: center;

    ${props => (props.show ? 'opacity: 1;' : 'opacity: 0;')}
`;

const TooltipButton = styled.button`
    border-radius: 3px;

    position: absolute;
    left: calc(100% - 35px);
    top: 5px;
    width: 30px;
    height: 30px;
    margin-top: 3px;
    margin-right: 3px;
    text-align: center;
`;

class TooltipContainer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show: false
        };
    }

    handleClick = () => {
        const { show } = this.state;
        this.setState({
            show: !show
        });
    };

    render() {
        const { message } = this.props;
        const { show } = this.state;
        return (
            <>
                <Tooltip show={show}>{message}</Tooltip>
                <TooltipButton onClick={this.handleClick}>
                    <i className="fas fa-info-circle" />
                </TooltipButton>
            </>
        );
    }
}

export default TooltipContainer;
