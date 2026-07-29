 const btnn = document.getElementById('btnn');
     const micBtn = document.getElementById("micBtn");
     const notificationBtn =
document.getElementById("notificationBtn");

const profilePic =
document.getElementById("profilePic");

const profilePanel =
document.getElementById("profilePanel");

const closeProfile =
document.getElementById("closeProfile");

const notificationPanel =
document.getElementById("notificationPanel");

const closeNotification =
document.getElementById("closeNotification");

const notificationList =
document.getElementById("notificationList");

const SpeechRecognition =
window.SpeechRecognition ||
window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();

recognition.lang = "en-IN";
recognition.continuous = false;
recognition.interimResults = false;
    loadProfile();
    async function loadProfile(){
 try{

    const response = await fetch(
      "http://127.0.0.1:5000/profile",
      {
        credentials:"include"
      }
    );

    const data = await response.json();

    if(data.success){

      document.getElementById('header').innerText =
        "Welcome, " + data.name;

      document.getElementById('studentName').innerText =
        data.name;

      document.getElementById('studentPin').innerText =
        data.pin;

      document.getElementById('studentBranch').innerText =
        data.branch;

      document.getElementById('studentAttendance').innerText =
        data.attendance + "%";
    }

    else{
      window.location.href = "login.html";
    }

  }
  catch(err){
    console.log(err);
  }

      // try{
      //   const response = await fetch("http://127.0.0.1:5000/profile",{
      //     credentials:"include"
      //   });
      //   const data = await response.json();
      //   if(data.success){
      //     document.getElementById('header').innerText="Welcome, "+data.name;
      //   }
      //   else{
      //     window.location.href="login1.html";
      //   }
      // }
      // catch(err){
      //   console.log(err);
      // }
    }
    
    const inputbar = document.getElementById('inputbar');
    const chatContainer = document.getElementById('chatContainer');
    
    inputbar.addEventListener('input', () =>{
      inputbar.style.height = 'auto';
      inputbar.style.height=inputbar.scrollHeight + 'px';
    });

    btnn.addEventListener('click',sendMessage);
    inputbar.addEventListener('keydown',function(e){
      if(e.key === 'Enter' && !e.shiftKey){
        e.preventDefault();
        sendMessage();
      }
    });
 micBtn.addEventListener("click",()=>{

   setVoiceState("listening");

recognition.start();

});
recognition.onresult=function(event){

    const speechText =
    event.results[0][0].transcript;

    inputbar.value=speechText;

    setVoiceState("thinking");

    sendMessage();

}
recognition.onerror = function(event){

    alert("Voice Error : " + event.error);

};
recognition.onend=function(){

    console.log("Recognition Ended");

};
notificationBtn.addEventListener("click",()=>{

    loadNotifications();

    notificationPanel.classList.add("active");

    profilePanel.classList.remove("active");

});

closeNotification.addEventListener("click",()=>{

    notificationPanel.classList.remove("active");

});
async function loadNotifications(){

    notificationList.innerHTML =
    "<p style='padding:20px'>Loading...</p>";

    const response = await fetch(
        "http://127.0.0.1:5000/notifications",
        {
            credentials:"include"
        }
    );

    const data = await response.json();

    notificationList.innerHTML="";

    data.notifications.forEach(note=>{

        notificationList.innerHTML += `

        <div class="notification-card">

            <div class="notification-category">

                ${note.category}

            </div>

            <div class="notification-title">

                ${note.title}

            </div>

            <div class="notification-message">

                ${note.message}

            </div>

            <div class="notification-date">

                ${new Date(note.created_at)
                    .toLocaleDateString()}

            </div>

        </div>

        `;

    });

}
profilePic.addEventListener("click",()=>{
    profilePanel.classList.add("active");
});

closeProfile.addEventListener("click",()=>{
    profilePanel.classList.remove("active");
});

    //  document.getElementById('logoutBtn').addEventListener('click',logoutStudent);
    async function logoutStudent() {
      await fetch("http://127.0.0.1:5000/logout",{
        method:"POST",
        credentials:"include"
      });
      window.location.href="login1.html";
      
    }
    function createTimeTable(title, rows){

    let html = `<h3>${title}</h3>`;

    html += `
    <table class="marks-table">
        <tr>
            <th>Day</th>
            <th>P1</th>
            <th>P2</th>
            <th>P3</th>
            <th>P4</th>
            <th>P5</th>
            <th>P6</th>
            <th>P7</th>
        </tr>
    `;

    // Group by day
    const timetable = {};

    rows.forEach(row => {

        if(!timetable[row.day_name]){
            timetable[row.day_name] = {};
        }

        timetable[row.day_name][row.period_no] = row.subject;

    });

    // Create rows
    for(let day in timetable){

        html += `
        <tr>
            <td>${day}</td>
            <td>${timetable[day][1] || "-"}</td>
            <td>${timetable[day][2] || "-"}</td>
            <td>${timetable[day][3] || "-"}</td>
            <td>${timetable[day][4] || "-"}</td>
            <td>${timetable[day][5] || "-"}</td>
            <td>${timetable[day][6] || "-"}</td>
            <td>${timetable[day][7] || "-"}</td>
        </tr>
        `;
    }

    html += `</table>`;

    return html;
}
 
      async function sendMessage(){
      document.getElementById('header').style.display = 'none';
      const userText = inputbar.value.trim();
      if(userText == '') return;
      appendMessage(userText,'user');
      const typingMessage = appendMessage("Bot is Thinking....","bot");
      inputbar.value='';
  

      // fetch('http://127.0.0.1:5000/chat',{
      //   method:'POST',
      //   headers: {'Content-Type':'application/json'},
      //   body: JSON.stringify({message: userText})
      // })

      // const response = await fetch(
      //   "http://127.0.0.1:5000/chat",
      //   {
      //     method : "POST",
      //     headers:{
      //       "Content-Type":"application/json"
      //     },
      //     credentials:"include",
      //     body:JSON.stringify({
      //       message:userText
      //     })
      //   }
      // )

      try{

    const response = await fetch(
        "http://127.0.0.1:5000/chat",
        {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },
            credentials:"include",
            body:JSON.stringify({
                message:userText
            })
        }
    );
    const data = await response.json();
    console.log(data);
    if (data.url){
      typingMessage.innerHTML = `${data.reply} <a href="${data.url}" target="_blank">${data.link_text}</a>`;
      setVoiceState("ready");
      return;
    }
    if(data.type === "timetable"){
    typingMessage.innerHTML =
        createTimeTable(data.title,data.data);
        setVoiceState("ready");
    return;
}
if(data.type === "sbtet_result"){

    typingMessage.innerHTML = `
        <h3>${data.title}</h3>

        <p><b>Name:</b>
        ${data.data.name}</p>
        <p><b>Branch:</b>
        ${data.data.branch}</p>

        <p><b>Grand Total:</b>
        ${data.data.grand_total}</p>

        <p><b>GPA:</b>
        ${data.data.gpa}</p>

        <p><b>Result:</b>
        ${data.data.result}</p>
    `;
    setVoiceState("ready");

    return;
}
if(data.type === "teachers"){
    typingMessage.innerHTML =
        createTeachersTable(data.title,data.data);
        setVoiceState("ready");
    return;
}
if(data.type==="today_classes"){
    typingMessage.innerHTML =
    createTodayClasses(data.title,data.data);
    setVoiceState("ready");
    return;
}
        // if(data.type.includes("table") || data.type==="MID_Marks")
        if(data.type){
          typingMessage.innerHTML = createTable(data.title,data.data,data.type);
          setVoiceState("ready");
          return;
        }
        //Full marks table display
    // if(data.type === "table"){
    //   typingMessage.innerHTML=createTable(data.title,data.data);
    // }
    else{
    // typingMessage.innerHTML =
    //     data.reply
    //     .replace(/\*\*(.*?)\*\*/g,'<b>$1</b>')
    //     .replace(/\n/g,'<br>');
    let reply = data.reply
    .replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank">$1</a>'
    )
    .replace(/\*\*(.*?)\*\*/g,'<b>$1</b>')
    .replace(/\n/g,'<br>');

typingMessage.innerHTML = reply;
    }

}
catch(err){

    typingMessage.innerHTML =
        "Error: Could not reach server";

    console.log(err);

}
      }





function createTeachersTable(title,rows){

    let html = `<h3>${title}</h3>`;

    html += `
    <table class="marks-table">
        <tr>
            <th>Subject</th>
            <th>Faculty</th>
            <th>Code</th>
        </tr>
    `;

    rows.forEach(row=>{
        html += `
        <tr>
            <td>${row.subject}</td>
            <td>${row.staff_name}</td>
            <td>${row.subject_code}</td>
        </tr>
        `;
    });

    html += `</table>`;

    return html;
}
function createTodayClasses(title, rows){

    let html = `<h3>${title}</h3>`;

    html += `
    <table class="marks-table">
        <tr>
            <th>Period</th>
            <th>Subject</th>
        </tr>`;

    rows.forEach(row=>{
        html += `
        <tr>
            <td>P${row.period_no}</td>
            <td>${row.subject}</td>
        </tr>`;
    });

    html += `</table>`;

    return html;
}
const voiceStatus =
document.getElementById("voiceStatus");

function setVoiceState(state){

    micBtn.classList.remove(

        "listening",

        "thinking"

    );

    switch(state){

        case "ready":

            voiceStatus.innerHTML="Ready";

            break;

        case "listening":

            micBtn.classList.add("listening");

            voiceStatus.innerHTML="🎤 Listening...";

            break;

        case "thinking":

            micBtn.classList.add("thinking");

            voiceStatus.innerHTML="🧠 Thinking...";

            break;

    }

}
      function createTable(title, rows, type){
        let html = `<h3>${title}</h3>`;
        html += `<table class="marks-table">`;

          if(type ==="MID-1_Marks"){
            html += `
            <tr>
              <th>Subject</th>
              <th>MID-1</th>
              <th>MID-1_AVG</th>
              </tr>`;
          }
          else if(type==="MID-2_Marks"){
             html += `
            <tr>
              <th>Subject</th>
              <th>MID-2</th>
              <th>MID-2_AVG</th>
              </tr>`;
          }
          else{
            html += `
            <tr>
              <th>Subject</th>
              <th>MID-1</th>
              <th>MID-2</th>
              <th>Final Average</th>
            </tr>`;
          }
          rows.forEach(row=>{
            if(type==="MID-1_Marks"){
              html += `
              <tr>
                <td>${row.subject}</td>
                <td>${row.mid1}</td>
                <td>${row.mid1_avg}</td>
                </tr>`; 
            }
            else if(type==="MID-2_Marks"){
              html +=  `
              <tr>
                <td>${row.subject}</td>
                <td>${row.mid2}</td>
                <td>${row.mid2_avg}</td>
                </tr>`;
            }
            else{
              html +=`
              <tr>
                <td>${row.subject}</td>
                <td>${row.mid1}</td>
                <td>${row.mid2}</td>
                <td>${row.final_avg}</td>
                </tr>`;
              }
            });
            html += `</table>`;
            return html;
      }
     
        //Full marks table display
      // function createTable(title,rows){
      //   let html = `<h3>${title}</h3>
      //     <table class="marks-table">
      //       <tr>
      //         <th>Subject</th>
      //         <th>MID-1</th>
      //         <th>MID-2</th>
      //         <th>Average</th>
      //         </tr>`;
      //         rows.forEach(row =>{
      //           html += `
      //           <tr>
      //             <td>${row.subject}</td>
      //             <td>${row.mid1}</td>
      //             <td>${row.mid2}</td>
      //             <td>${row.final_avg}</td>
      //             </tr>`;
      //         });
          
         
      //     html +=`</table>`;
      //     return html;
      // }


    //   .then(res => res.json())
    //   .then(data => {
    //     typingMessage.innerHTML = data.reply.replace(/\*\*(.*?)\*\*/g,'<b>$1</b>').replace(/\n/g,'<br>');
    //   })
    //   .catch(err => {
    //     appendMessage('Error: Could not reach server', 'bot');
    //   });
    // }
    //   setTimeout(()=>{
    //     appendMessage('You Said ' + userText, 'bot');
    //   },500);
    // };

    function appendMessage(text, sender){
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('message',sender);
      msgDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g,'<b>$1</b>').replace(/\n/g,'<br>');
      chatContainer.appendChild(msgDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
      return msgDiv
    }
