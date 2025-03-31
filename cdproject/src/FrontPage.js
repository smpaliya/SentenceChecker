import React, { useState } from 'react';
import './FrontPage.css'
function FrontPage(){
    const [sentence,SetSent]=useState("");
    const[res,SetRes]=useState(false);
    const[loadResult,SetLoadResult]=useState(false);
    const handleFormSubmit=async(event)=>{
        event.preventDefault();
        const sentence2=sentence.toLowerCase()
        try{
            const response=await fetch("http://localhost:5000/checksentence",{
            method:"POST",
            headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({"sentence":sentence2}),}
        )
        const data = await response.json(); // Get response data
        if(response.ok){
            alert("sent");
        }
          if (!response.ok) {
             console.log(data.error);
              throw new Error(data.error || 'Failed to send');
          }
          console.log(data);
          alert(data.message);
          SetRes(data.answer);
          SetLoadResult(true);
      } catch (error) {
          console.error('Error:', error.message);
      }
    };
  
    return(
        <>
    <header>
	<div class="overlay">
<h1 className='head1'>Sentence Checker</h1>
<h3>Using LL1 parser</h3>
<p>Considers words from given set of grammar:"Article": [["a"], ["the"]],"Noun": [["cat"], ["dog"], ["man"], ["woman"],["ship"],["bird"]],"Verb": [["eats"], ["sees"], ["likes"],,["speaks"],["floats"],["flew"]]</p><br></br>
		</div>
</header>
<form className='inputform'>
    <label className='label1'>Enter a Sentence</label>
    <br></br>
    <input type='textarea'className='inputsentence' onChange={e=>SetSent(e.target.value)}></input>
    <br></br>
    <center><button type='submit' onClick={handleFormSubmit}>Submit</button></center>
</form>
{loadResult && (
    res ? (
        <h1 className='output'>✅ It is a valid Sentence!</h1>
    ) : (
        <h1  className='output'>❌ It is not a valid Sentence!</h1>
    )
)}
</>
)
}
export default FrontPage;