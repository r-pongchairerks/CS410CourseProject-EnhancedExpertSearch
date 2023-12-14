var startResults = 5;
var numResults = startResults;
var incResults = 5;

var selected_loc_filters = []
var selected_uni_filters = []
var searchTerm = ''


const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;
const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}
const generateResponse = (chatElement) => {
    // const API_URL = "https://api.openai.com/v1/chat/completions";
    const messageElement = chatElement.querySelector("p");
    // // Define the properties and message for the API request
    fetch("http://localhost:8095/chat", {
        method: "POST",
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },


        body: JSON.stringify({"query": userMessage,
                                "num_results": numResults,
                                "selected_loc_filters" : selected_loc_filters,
                                "selected_uni_filters": selected_uni_filters})
    }).then(res => res.json()).then(data => {
        messageElement.textContent = data.docs;
    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}
const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if(!userMessage) return;
    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;
    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);
    
    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}
chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});
chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window 
    // width is greater than 800px, handle the chat
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});
sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));

var docDiv = (doc) => {
    const name = doc[0];
    const prev = doc[1];
    const email = doc[2];
    const uni_dept = doc[4]+', '+doc[3]
    const fac_name = doc[5]
    const fac_url = doc[6]
    const loc = doc[7]+', '+doc[8]



    if (email =='None') {
        return (
             `<div class="card">
             <div class="card-header">
       <div style="display: flex;">

        
                 <b style="font-size:14pt">${fac_name}</b>
                 <a style="margin-left:auto;color:black;" href=${fac_url} target="_blank"><i class="material-icons">launch</i></a>
                 </div>

            <div class="header-item">
            <div class="tag">
            <i class='fas fa-university' ></i>
                  ${uni_dept}
            </div>
                <div class="tag">
                  <i class="material-icons">location_on</i>
                   ${loc}
                 </div>
            </div>
            </div>
           

              <div class="card-body">
                <span id='docPrev-${name}'>${prev}</span>
                <br>
            </div>
            </div>`
        );
    } else {
        return (
            `<div class="card">
             <div class="card-header">
       <div style="display: flex;">

        
                 <b style="font-size:14pt">${fac_name}</b>
                 <a style="margin-left:auto;color:black;margin-right:20px;" href='mailto:${email}' "><i class="material-icons">email</i></a>
                 <a style="color:black;" href=${fac_url} target="_blank"><i class="material-icons">launch</i></a>
                 </div>

            <div class="header-item">
            <div class="tag">
            <i class='fas fa-university' ></i>
                  ${uni_dept}
            </div>
                <div class="tag">
                  <i class="material-icons">location_on</i>
                   ${loc}
                 </div>
            </div>
            </div>
         

              <div class="card-body">
                <span id='docPrev-${name}'>${prev}</span>
                <br>
            </div>
            </div>`
        );
    }
}

var doSearch = function() {
    const data = {
        "query": searchTerm,
        "num_results": numResults,
        "selected_loc_filters" : selected_loc_filters,
        "selected_uni_filters": selected_uni_filters
    }
    if (searchTerm!='')
    {
    var num_fetched_res = 0
    fetch("http://localhost:8095/search", {
    // fetch("http://expertsearch.centralus.cloudapp.azure.com/search", {
        method: "POST",
        headers: {
            "Access-Control-Allow-Origin": "http://localhost:8095",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    }).then(response => {
        response.json().then(data => {
            const docs = data.docs;
            $("#docs-div").empty();

            docs.forEach(doc => {
            
                $("#docs-div").append(
                    docDiv(doc)
                );
                    num_fetched_res = num_fetched_res+1;

            });
          
            if (num_fetched_res==numResults){

            $("#loadMoreButton").css("display", "block")
        }
        else{
            $("#loadMoreButton").css("display", "none")
        }
        if (num_fetched_res==0){
            $("#docs-div").append(`<h3 style="text-align: center;margin-top:20px;">No Search Results Found</h3>`);
        }
        })

    });
}
}

$(window).on("resize",function() {
    $(document.body).css("margin-top", $(".navbar").height()+5 );
    var width = $(".select2-container").width()
    if ((width == 0)||width===undefined){
        width = 300
    }
    $(".select2-search__field").css('cssText', $(".select2-search__field").attr('style')+'width: ' + width+ 'px !IMPORTANT;');
}
).resize();


$(document).ready(function() {
    $('#loc_filter').select2({placeholder: "e.g. United States, California"});
    $('#uni_filter').select2({placeholder: "e.g. Stanford University"});
    $(window).trigger('resize');
});

window.onload=function(){
    for (var i=0;i<unis.length;i++){
         var newOption = new Option(unis[i], i, false, false);
        // Append it to the select
        $('#uni_filter').append(newOption).trigger('change');
       

    }
    selected_uni_filters = unis.slice()
    for (var i=0;i<locs.length;i++){
         var newOption = new Option(locs[i], i, false, false);
        // Append it to the select
        $('#loc_filter').append(newOption).trigger('change');
    }
    selected_loc_filters = locs.slice()
    $(window).trigger('resize');
 
};

function  toggleFilter() {
  filters_div = document.getElementById("search-filters")
  filters_div.style.display = filters_div.style.display=== 'none' ? 'flex' : 'none';
}

$("#submitButton").click(function() {
    numResults = startResults;
    searchTerm = $('#query').val()
    doSearch();
});

$("#filterButton").click(function() {
    toggleFilter();
});

$('#query').keydown(function(e) {
    searchTerm = $('#query').val()
    if (e.keyCode == 13) {
        numResults = startResults;
    
    doSearch();
    }
});

$("#applyFilters").click(function() {
  
    var selected_uni_data = $("#uni_filter").select2("data");
    selected_uni_filters = []
    selected_uni_data.forEach(s => {
            selected_uni_filters.push(s['text']);

});
      
    if (selected_uni_filters.length== 0){
        selected_uni_filters = unis.slice()
    }

    var selected_loc_data = $("#loc_filter").select2("data");
    selected_loc_filters = []
    selected_loc_data.forEach(s => {
            selected_loc_filters.push(s['text']);

});

    if (selected_loc_filters.length == 0){
        selected_loc_filters = locs.slice()
    }
  filters_div = document.getElementById("search-filters")
  filters_div.style.display = 'none'
        doSearch();
    });

$("#settingsButton").click(function() {
   window.location = "http://localhost:8095/admin"
});

$("#loadMoreButton").click(function() {
    numResults += incResults

    doSearch();
});