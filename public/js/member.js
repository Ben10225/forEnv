// fetchMsg(false);

let btn = document.querySelector("button")
btn.addEventListener("click", ()=>{
  fetchMsg(true);
});


function fetchMsg(bool){
  let msg = document.querySelector("#stayMsg");
  fetch("/message", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "msg": msg.value,
      "click": bool,
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    if(data.result=="請留言"){
      alert("請輸入文字")
    }else{
      // window.location.href="/member";
      msg.value = "";
      // let msgBoardInner = document.querySelector(".msgBoard")
      // let txt = "";
      // for(let i=0;i<data.result.length;i++){
      //   let time = data.result[i][2].split(" ")
      //   time = `${time[4].slice(0,5)}`
      //   txt +=`
      //   <div class="row d-flex justify-content-center mt-1">
      //     <div class="col-6 text-start msg">
      //       <h4 class="userName">${data.result[i][0]}</h4>
      //       <h4 class="userMsg">:&emsp;${data.result[i][1]}</h4>
      //       <h4 class="userTime">${time}</h4>
      //     </div>
      //   </div>
      //   `;
      //   msgBoardInner.innerHTML = txt;
      
    }
  })
}
