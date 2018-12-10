function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
	//发送ajax请求
	//请求house的详细信息
	var url = "/api/v1.0/houses/"+decodeQuery()["house_id"];
	$.get(url,function(data){
		if("0" == data.errorno){
			//处理
			var house = data.data.house;
			visit_id = data.data.user_id;
			house_user_id = house.user_id;
			var html = template("body",{house:house});
			$(".container").html(html);
			if(visit_id == house_user_id){
    			$(".book-house").hide();
			}else{
    			$(".book-house").show();
				$(".book-house").attr("href","/booking.html?house_id="+house.house_id);
			}
			var mySwiper = new Swiper ('.swiper-container', {
        		loop: true,
	        	autoplay: 2000,
    	    	autoplayDisableOnInteraction: false,
        		pagination: '.swiper-pagination',
        		paginationType: 'fraction',
    		});
		}else{
			alert(data.errormsg)
		}	
	},"json");
    });
