function getCookie(name) {
       var r = document.cookie.match("\\b" + name  + "=([^;]*)\\b");
       return r ? r[1] : undefined;
  }

function logout() {
	// 发送ajax请求
	// 方式delete
	var url = "/api/v1.0/session";
	$.ajax({
		url:url,
		type:"delete",
		dataType:"json",
		headers:{
			"X-CSRFToken":getCookie("csrf_token"),
			},
		success:function(data){
			if("0" == data.errorno){
				location.href = "/index.html";
			}else{
				alert(data.errormsg);
			}
	}
	});
}

$(document).ready(function(){
	//请求用户信息
	//如没有登录，跳转到首页
	//否者正常显示信息
	//发起ajax请求
	var url = "/api/v1.0/users";
	$.get(url,function(data){
		if ("4101" == data.errorno){
			location.href = "/login.html";	
		}
		if("0" == data.errorno){
			$("#user-name").html(data.data.user_name);
			$("#user-mobile").html(data.data.user_mobile);
			$("#user-avatar").attr('src',data.data.url);
		}else{
			alert(data.errormsg);
		}
	},"json");
})
