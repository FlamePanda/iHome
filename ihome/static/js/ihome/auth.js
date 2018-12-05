function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
     var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
     return r ? r[1] : undefined;
 }

$(document).ready(function(){
	//请求用户实名信息
	var url = "/api/v1.0/users/auth";
	$.get(url,function(data){
		//判断用户是否登录
		if(data.errorno == "4101"){
			location.href="/login.html";
		}
		if('0' == data.errorno){
			if(data.data.name != "" || data.data.id_card != ""){
			//设置input输入框不能修改
			$("#real-name").prop("disabled",true);
			$("#id-card").prop("disabled",true);
			//隐藏提交按钮
			$("input[type='submit']").hide();}
			$("#real-name").val(data.data.name);
			$("#id-card").val(data.data.id_card);
		}else{
			alert(data.errormsg);
		}
	},"json");
	//修改用户实名信息		
	$("#form-auth").submit(function(e){
		e.preventDefault();
	var real_name = $("#real-name").val().trim();
	var id_card = $("#id-card").val().trim();

		if(real_name == '' || id_card == ''){
			alert("真实姓名或身份证号不能为空！");	
			return
		}

		var params = {'real_name':real_name,'id_card':id_card};
		var data = JSON.stringify(params);
		$.ajax({
			url:url,
			data:data,
			type:"post",
			dataType:"json",
			contentType:"application/json",
			headers:{
			"X-CSRFToken":getCookie("csrf_token"),
			},
			success:function(data){
			//判断用户是否登录
			if(data.errorno == "4101"){
				location.href="/login.html";
			}
			if('0' == data.errorno){
			showSuccessMsg();
			//设置input输入框不能修改
			$("#real-name").prop("disabled",true);
			$("#id-card").prop("disabled",true);
			//隐藏提交按钮
			$("input[type='submit']").hide();
				}else{
					alert(data.errormsg)
				}
			}
		});
	});
});
