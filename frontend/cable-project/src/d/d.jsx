import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import styles from "./d.module.css";
import { Navbar } from "../navbar/navbar";

export const D = () => {
  const history = useNavigate();
  const [formData, setFormData] = useState({
    measurement_id: '',
    start_year: '',
    start_month: '',
    start_day: '',
    end_year: '',
    end_month: '',
    end_day: ''
  });

  const [isLoading, setIsLoading] = useState(false); 
  const [isSubmitted, setIsSubmitted] = useState(false); 

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); 
    try {
      const response = await fetch('http://127.0.0.1:5000/d', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        console.log('Form submitted successfully!');
        setIsSubmitted(true); 
      } else {
        console.error('Failed to submit form:', response.statusText);
      }
    } catch (error) {
      console.error('Error submitting form:', error.message);
    } finally {
      setIsLoading(false); 
    }
  };

  return (
    <>
      <Navbar />
      <div className={styles['form-container']}>
        <h2>Anomalies for station</h2>
        <form onSubmit={handleSubmit}>
          <div className={styles['form-group']}>
            <label>Measurement ID:</label>
            <input type="text" name="measurement_id" value={formData.measurement_id} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}><label>Introduce the start date for the collecting of data:</label></div>
          <div className={styles['form-group']}>
            <label>Year</label>
            <input type="text" name="start_year" value={formData.start_year} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}>
            <label>Month</label>
            <input type="text" name="start_month" value={formData.start_month} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}>
            <label>Day</label>
            <input type="text" name="start_day" value={formData.start_day} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}><label>Introduce the end date for the collecting of data:</label></div>
          <div className={styles['form-group']}>
            <label>Year</label>
            <input type="text" name="end_year" value={formData.end_year} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}>
            <label>Month</label>
            <input type="text" name="end_month" value={formData.end_month} onChange={handleChange} />
          </div>
          <div className={styles['form-group']}>
            <label>Day</label>
            <input type="text" name="end_day" value={formData.end_day} onChange={handleChange} />
          </div>
          {isLoading ? (
            <div className={styles['loading']}>Loading...</div>
          ) : isSubmitted ? (
            <button type="button" className={styles['submit-button']} onClick={() => history('/d_res')}>See Results</button>
          ) : (
            <button type="submit" className={styles['submit-button']}>Submit</button>
          )}
        </form>
      </div>
    </>
  );
};

export default D;
