import React, { useState, useEffect } from 'react';
import styles from "./form.module.css";
import { Navbar } from "../navbar/navbar";
import { useNavigate } from 'react-router-dom';

export const Form = () => {
  const history = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [formData, setFormData] = useState({
    measurement_id: '',
    start_year: '',
    start_month: '',
    start_day: '',
    end_year: '',
    end_month: '',
    end_day: '',
    id: ''
  });

  useEffect(() => {
    let timer;
    if (isLoading) {
      timer = setInterval(() => {
        setElapsedTime(prevTime => prevTime + 1);
      }, 1000);
    } else {
      clearInterval(timer);
      setElapsedTime(0);
    }
    return () => clearInterval(timer);
  }, [isLoading]);

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
      const response = await fetch('http://127.0.0.1:5000/run', {
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
        <h2>See delays and insights of a measurement</h2>
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
          <div className={styles['form-group']}>
            <label>Introduce the ID of the delay you want to see additional information for:</label>
            <input type="text" name="id" value={formData.id} onChange={handleChange} />
          </div>
          {isLoading ? (
            <>
              <div className={styles['loading']}>Loading...</div>
              <div className={styles['elapsed-time']}>Time elapsed since submitting: {elapsedTime} seconds</div>
            </>
          ) : isSubmitted ? (
            <button type="button" className={styles['submit-button']} onClick={() => history('/param')}>See Results</button>
          ) : (
            <button type="submit" className={styles['submit-button']}>Submit</button>
          )}
        </form>
      </div>
    </>
  );
};

export default Form;
