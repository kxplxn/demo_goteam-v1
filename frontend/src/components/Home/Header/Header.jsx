import React from 'react';
import PropTypes from 'prop-types';
import { Container, Row } from 'react-bootstrap';
import {
  faChalkboardTeacher, faUsers,
} from '@fortawesome/free-solid-svg-icons';

import ControlsToggler from './ControlsToggler/ControlsToggler';
import HelpToggler from './HelpToggler/HelpToggler';
import { windowEnum } from '../windowEnum';

import logo from '../../../assets/home.svg';
import './header.sass';

const Header = ({ activeWindow, handleActivate }) => (
  <div id="Header">
    <div className="Logo">
      <img alt="logo" src={logo} />
    </div>
    <div className="ControlsWrapper">
      <Container>
        <Row className="ControlsRow">
          <ControlsToggler
            name="team"
            isActive={activeWindow === windowEnum.TEAM}
            activate={handleActivate(windowEnum.TEAM)}
            create={handleActivate(windowEnum.INVITE_MEMBER)}
            icon={faUsers}
          />

          <ControlsToggler
            name="boards"
            isActive={activeWindow === windowEnum.BOARDS}
            activate={handleActivate(windowEnum.BOARDS)}
            create={handleActivate(windowEnum.CREATE_BOARD)}
            icon={faChalkboardTeacher}
          />

          <HelpToggler toggle={handleActivate(windowEnum.MODAL)} />
        </Row>
      </Container>
    </div>
  </div>
);

Header.propTypes = {
  activeWindow: PropTypes.number.isRequired,
  handleActivate: PropTypes.func.isRequired,
};

export default Header;