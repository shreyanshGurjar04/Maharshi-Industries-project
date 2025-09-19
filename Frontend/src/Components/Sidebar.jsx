import React from 'react'
import './style.css';
import set from '../assets/settings.png'
import blackli from '../assets/BlackList.png';
import whiteli from '../assets/WhiteList.png'
import detect from '../assets/Detection.png';
import dash from '../assets/dashboard.png';
import analyst from '../assets/analytics.png';
import logo from '../assets/logo.png';
import vid from '../assets/Play.png';
import { useNavigate } from 'react-router-dom';

function Sidebar() {
  const navigate = useNavigate();

  return (
    <div className='sidebar'>

        <div className='logo'>
            <img className='lo' src={logo} alt="logo" />
            <h3><b>ANPR System</b></h3>
        </div>

        <div className='button-array'>

            <div className='btn dashboard'>
                <img className='detection' src={dash} alt="dashboard" />
                <button onClick={() => navigate('/')}>Dashboard</button>
            </div>

            <div className='btn dashboard'>
                <img className='detection' src={analyst} alt="analytics" />
                <button onClick={() => navigate('/analytics')}>Analytics</button>
            </div>

            <div className='btn detect'>
                <img className='de' src={detect} alt="detection" />
                <button onClick={() => navigate('/detection')}>Detections</button>
            </div>

            <div className='btn blacklisted'>
                <img className='blacklist' src={blackli} alt="blacklist" />
                <button onClick={() => navigate('/blacklist')}>BlackList</button>
            </div>

            <div className='btn whitelisted'>
                <img className='whitelist' src={whiteli} alt="whitelist" />
                <button onClick={() => navigate('/whitelist')}>WhiteList</button>
            </div>

            <div className='btn video'>
                <img className='videoplay' src={vid} alt="whitelist" />
                <button onClick={() => navigate('/videoplayback')}>Video Playback</button>
            </div>
                
        </div>

    </div>
  )
}

export default Sidebar
