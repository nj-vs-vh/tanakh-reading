
const themes = {
    Стандартная: {
        color: {
            background: 'white',
            text: '#242424',
            text_tinted: '#454545',
            border: '#626262',
            secondary: {
                background: '#e1e1e1',
                text: '#868686',
                border: '#c1c1c1',
            },
            bad: '#7e0000',
            bookmark: {
                active: '#c6a059',
                potential: 'rgb(200, 200, 200)'
            },
            user_comment: {
                active: "#44B2C3",
                potential: 'rgb(200, 200, 200)'
            },
            clickable_text: {
                clickable: '#efefef',
                hovered: '#e3e3e3'
            }
        }
    },
    Тёмная: {
        color: {
            background: '#21252B',
            text: '#b2b2b2',
            text_tinted: '#929496',
            border: '#c2c4ce',
            secondary: {
                background: '#12151a',
                text: '#6f767e',
                border: '#5c6474',
            },
            bad: '#7e0000',
            bookmark: {
                active: '#AA5236',
                potential: '#495162'
            },
            user_comment: {
                active: "#3084B2",
                potential: '#495162'
            },
            clickable_text: {
                clickable: '#2c313a',
                hovered: '#414750'
            }
        }
    }
}

export default themes;