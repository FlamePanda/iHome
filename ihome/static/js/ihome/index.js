//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function setStartDate() {
    var startDate = $("#start-date-input").val();
    if (startDate) {
        $(".search-btn").attr("start-date", startDate);
        $("#start-date-btn").html(startDate);
        $("#end-date").datepicker("destroy");
        $("#end-date-btn").html("离开日期");
        $("#end-date-input").val("");
        $(".search-btn").attr("end-date", "");
        $("#end-date").datepicker({
            language: "zh-CN",
            keyboardNavigation: false,
            startDate: startDate,
            format: "yyyy-mm-dd"
        });
        $("#end-date").on("changeDate", function() {
            $("#end-date-input").val(
                $(this).datepicker("getFormattedDate")
            );
        });
        $(".end-date").show();
    }
    $("#start-date-modal").modal("hide");
}

function setEndDate() {
    var endDate = $("#end-date-input").val();
    if (endDate) {
        $(".search-btn").attr("end-date", endDate);
        $("#end-date-btn").html(endDate);
    }
    $("#end-date-modal").modal("hide");
}

function goToSearchPage(th) {
    var url = "/search.html?";
    url += ("aid=" + $(th).attr("area-id"));
    url += "&";
    var areaName = $(th).attr("area-name");
    if (undefined == areaName) areaName="";
    url += ("aname=" + areaName);
    url += "&";
    url += ("sd=" + $(th).attr("start-date"));
    url += "&";
    url += ("ed=" + $(th).attr("end-date"));
    location.href = url;
}

$(document).ready(function(){
    	//发送ajax请求
	//请求用户登录状态
	var url = '/api/v1.0/session';
	$.get(url,function(data){
		if('0' == data.errorno){
			//显示用户登录信息
    	$(".top-bar>.user-info").show();
		$(".user-name").html(data.data);	
		}else{
    	$(".top-bar>.register-login").show();
		}
	});
	//
	//发送ajax请求
	//请求城区信息
	$.get("/api/v1.0/areas",function(data){
		if("0" == data.errorno){
			//展现城区信息
			var areas = data.areas;
			var html = template("areasList",{areas:areas});
			$(".area-list").html(html);
			$(".area-list a").click(function(){
				var area_name = $(this).html();
				var area_id = $(this).attr("area-id");
   	        	$("#area-btn").html(area_name);
   	       	 	$(".search-btn").attr("area-id", area_id);
	        	$(".search-btn").attr("area-name", area_name);
	        	$("#area-modal").modal("hide");
	    	});
		}else{
			alert(data.errormsg);
		}
	},"json");

	//获取销量最多的房子图片
	//
	var url = "/api/v1.0/houses/indexImage";
	$.get(url,function(data){
		if("0" == data.errorno){
			//设置首页图片
			var images = data.data;
			var html = template("indexImages",{images:images});
			$(".swiper-wrapper").html(html);
			var mySwiper = new Swiper ('.swiper-container', {
        		loop: true,
  	        	autoplay: 2000,
	       		autoplayDisableOnInteraction: false,
    	    	pagination: '.swiper-pagination',
        		paginationClickable: true
    		}); 
		}else{
			alert(data.errormsg);
		}	
	},"json");


    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候
    $("#start-date").datepicker({
        language: "zh-CN",
        keyboardNavigation: false,
        startDate: "today",
        format: "yyyy-mm-dd"
    });
    $("#start-date").on("changeDate", function() {
        var date = $(this).datepicker("getFormattedDate");
        $("#start-date-input").val(date);
    });
})
