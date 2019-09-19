var input = document.querySelector("#input")
var heading = document.querySelector('#heading')
var timeContain = document.querySelector('#time')
var container1 = document.querySelector('.slide-main-container1')
var container2 = document.querySelector('.slide-main-container2')
var container3 = document.querySelector('.slide-main-container3')
var h1 = document.querySelector('#h1')
var button = document.querySelector('.button')
var time = 1
var name = ""
var counterContainer = document.querySelector('#counter')
var connect = function(type, url, data){
    type.toUpperCase()
    let request = new XMLHttpRequest()
    request.open(type, url)
    if(type == 'POST'){
        request.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
        request.send(data)

    }
    else if(type == 'GET'){
        request.onload = function(){
            var ourData = JSON.parse(request.responseText)
        }
        request.send()
        return ourData        
    }
}
var timeadd = function(){
    if(time <= 9){
        time = time + 1
    } 

}
var counter = function(){
    let time = 10
    setInterval(()=>{
        counterContainer.textContent = `Time left: ${time}`
        time --       
    if(time == 0){
        container2.id = "ispaused"
    }
    

    }, 1000)
}
var timedel = function(){
    if(time >= 2){
        time = time - 1
    }
}
input.addEventListener('input', (event)=>{
    
    if(event.target.value.toLowerCase() == 'vishal'){
        container1.id = "ispaused"
        name = event.target.value
        counter()

    }
    else if(event.target.value.length == 8){
        heading.textContent = "you are not my friend"
    }

})
document.body.addEventListener("keyup", (event)=>{
    if(event.keyCode == 38){
        timeadd()
    }
    else if(event.keyCode == 40){
        timedel()
    }
    timeContain.textContent = time
})
button.addEventListener('click', (event)=>{
    h1.textContent = 'You have fucked with wrong guy'
    h1.style.color = 'red'
    dataJson = `name=${name}&time=${time}`
    var url = 'http://localhost:8080/request'
    const xm = new XMLHttpRequest
    xm.onload = ()=>{
        console.log("done")
    }
    xm.open("POST", url)
    xm.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xm.send(dataJson)

})