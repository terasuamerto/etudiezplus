


function openLeft(){
    var left = document.getElementById("sidebar");
    left.style.display = "flex";
}

function progressBar(){
    var progressBar = document.getElementById("rightContent");
    if(progressBar.style.display==="none"){
        progressBar.style.display="flex";
    }else{
        progressBar.style.display="none";
    }
}

function closeLeft(){
    var left = document.getElementById("sidebar");
    var right = document.getElementById("rightContent");
    right.style.display = "none";
    left.style.display = "none";
}

$(window).resize(function(e){
    screen_resize();
});
function screen_resize(){
    var w = parseInt(window.innerWidth);

    var left = document.getElementById("sidebar");
    var flecheNormale = document.querySelector('.flecheNormale');
    var progressContent = document.getElementById("rightContent");
    if(w>=1126){
        left.style.display = "none";
        flecheNormale.style.display ="block";
        progressContent.style.display = "flex";
    }else if(w<1126){
        progressContent.style.display = "none";
    }

}


