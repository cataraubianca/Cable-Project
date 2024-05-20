import { useState } from 'react'
import { Case2 } from './case2/case2';
import { Case1 } from './case1/case1';
import { Form } from './form/form';
import { Param } from './param/param';
import { Delays } from './delays/delays';
import { Dw } from './dw/dw';
import { D } from './d/d';
import { D_res } from './d_res/d_res';
import './App.css'
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";

function App() {

  return (
    <>
       <>
        <Router>
          <Routes>
            <Route exact path="/case2" element={<Case2/>}/>
            <Route exact path="/case1" element={<Case1 />} />
            <Route exact path="/" element={<Form />} />
            <Route exact path="/param" element={<Param />} />
            <Route exact path="/delays" element={<Delays />} />
            <Route exact path="/dw" element={<Dw />} />
            <Route exact path="/d" element={<D />} />
            <Route exact path="/d_res" element={<D_res />} />
          </Routes>
        </Router>
      </>
    </>
  )
}

export default App
