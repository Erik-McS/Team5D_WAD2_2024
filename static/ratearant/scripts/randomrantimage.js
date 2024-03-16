// function in JSQuery to randomise some pics
$(document).ready(function (){
    // store the path to the image
    var pathToImage = staticUrl + "rateArant_";
    //get a number between 1-19
    var nums=19;
    var random=Math.floor(Math.random()*nums)+1;
    var image=pathToImage+random+".jpg";
    //console.log(image);
    $('#restaurantpic').attr('src',image);
});