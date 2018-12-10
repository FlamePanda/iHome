
$(document).ready(function(){
	//请求用户是否认证，
	//若没有认证，显示前往认证
	//若已认证，显示房主所有的房子
	var url = "/api/v1.0/users/auth";
	$.get(url,function(data){
		if("4101" == data.errorno){
			//重定向至登录页
			location.herf= "/login.html";
			return ;
		}else if("0" == data.errorno){
			if(data.data.name != "" && data.data.id_card != ""){
				//用户已实名	
    			$(".auth-warn").hide();
				$("#houses-list").show();
			}else{
    			$(".auth-warn").show();
				$("#houses-list").hide();
				return ;
			}
		}else{
			alert(data.errormsg);
			return ;
		}
	},"json");
	

	//请求用户房子信息
  	var url = "/api/v1.0/users/houses";
	$.get(url,function(data){
		if("4101" == data.errorno){
			location.herf = "/login.html";
		 } else if("0" == data.errorno){
			var houses = data.data.houses;
			var html = template("house",{houses:houses});
			$("#houses-list").append(html);
		}else{
			alert(data.errormsg);
		}		
	},"json");	
	
})
