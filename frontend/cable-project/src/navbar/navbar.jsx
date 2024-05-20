import React from 'react';
import { Link } from 'react-router-dom'; 
import styles from './Navbar.module.css'; 

export const Navbar = () => {
  return (
    <nav className={styles.navbar}>
      <ul className={styles.navbarNav}>
        <li className={styles.navItem}>
          <Link to="/" className={styles.navLink}>Full Insights</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/delays" className={styles.navLink}>Anomalies & Withdrawals</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/d" className={styles.navLink}>Anomalies</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/case1" className={styles.navLink}>Case 1</Link>
        </li>
        <li className={styles.navItem}>
          <Link to="/case2" className={styles.navLink}>Case 2</Link>
        </li>
      </ul>
    </nav>
  );
};

