import React from 'react';

import styled, { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        font-family: 'Merriweather', serif;
    }

    #root {
        height: 100%;
    }
`;

const Page = styled.div`
    background: #000000;
    height: 100%;
`;

const FlagRow = styled.div`
    background: #00ff00;
`;

const Component = ({ flags }) => (
    <>
        <GlobalStyle />
        <iframe
            src="https://panzi.github.io/Browser-Ponies/ponies-iframe.html#fadeDuration=500&volume=1&fps=25&speed=20&audioEnabled=false&dontSpeak=true&showFps=false&showLoadProgress=false&speakProbability=0.1&spawn.princess%20luna%20(season%201)=1&paddock=false&grass=false"
            style={{
                position: 'fixed',
                overflow: 'hidden',
                borderStyle: 'none',
                margin: 0,
                padding: 0,
                background: 'transparent',
                width: '100%',
                height: '100%'
            }}
            width="640"
            height="480"
            frameBorder="0"
            scrolling="no"
            marginHeight="0"
            marginWidth="0"
            title="pony"
        />
        <Page>
            {flags.map(({ attacker, victim, delta }, index) => (
                <FlagRow
                    key={index}
                >{`${attacker} stole ${delta} flag points from ${victim}`}</FlagRow>
            ))}
        </Page>
    </>
);

export default Component;
