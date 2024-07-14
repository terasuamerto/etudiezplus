var title1 = document.getElementById("title1");
var title2 = document.getElementById("title2");
var progressbar = document.getElementById("progression");

        var divInfos = document.getElementById('content1');
        var divInfos2 = document.getElementById('content2'); 
        var progressConetent = document.getElementById("rightContent");
          
         
        title1.onclick = function(){
            if(divInfos.style.display === "none"){
                divInfos.style.display = "block";
                
                
            }else{
                divInfos.style.display = "none";
                 
                
            }
        }

        title2.onclick = function(){
            if(divInfos2.style.display === "none"){
                divInfos2.style.display = "block";
                
                
            }else{
                divInfos2.style.display = "none";
                 
                
            }
        }

        // progressbar.onclick = function(){
        //     if(progressConetent.style.display === "none"){
        //         progressConetent.style.display = "block";
        //     }else{
        //         progressConetent.style.display === "none";
        //     }

        // }