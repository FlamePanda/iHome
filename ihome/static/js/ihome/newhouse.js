function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
	//动态获取所有的城区信息
	var url = "/api/v1.0/areas";
	$.get(url,function(data){
			if('0' == data.errorno){
				var areas = data.areas;
				//for(i=0;i<areas.length;i++){
				//var html = '<option value="'+areas[i].id+'">'+areas[i].name+'</option>';
				//$("#area-id").append(html);}
				//使用js模板渲染
				var html = template('areas-template',{areas:areas});
				$("#area-id").html(html);
			}else{
				alert(data.errormsg);
			}
	},"json");
	//动态获取所有的设施
	var url = "/api/v1.0/facility";
	$.get(url,function(data){
			if('4101' == data.errorno){
				location.href = "/login.html";	
			}
			else if('0' == data.errorno){
				var facilities = data.data.facilities;
				//alert(facilities);
				//使用js模板渲染
				var html = template('facility-template',{facilities:facilities});
				$(".house-facility-list").html(html);
			}else{
				alert(data.errormsg);
			}
	},"json");
	//提交house info		
		

	//发送请求
	$("#form-house-info").submit(function(e){
		e.preventDefault();
		var url = "/api/v1.0/houses";
		//获取所有的表单数据
		var data = {};
		$("#form-house-info").serializeArray().map(function(x){data[x.name] = x.value});
		//获取设施列表
		var facility_list = [];
		$(':checked[name="facility"]').each(function(index,x){facility_list[index] = $(this).val()});
		//重新设置facility
		data['facility'] = facility_list;
		var data = JSON.stringify(data);
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
			 if("4101" == data.errorno){
               location.href = "/login.html";
			}
				if('0' == data.errorno){
						//隐藏info表单
						$("#form-house-info").hide();
						//显示image表单
						$("#form-house-image").show();
						//设置house_id	
						$("#house-id").val(data.data.house_id);
					}else{
						alert(data.errormsg);
					}
			}
		});
	
	});
	//发送图片请求
	$("#form-house-image").submit(function(e){
		e.preventDefault();
		var url = "/api/v1.0/houses/images";
		$(this).ajaxSubmit({
			url:url,
			type:"post",
			dataType:"json",
			headers:{"X-CSRFToken":getCookie("csrf_token")},
			success:function(data){
				if("4101" == data.errorno){
					location.href="/login.html";
				}else if("0" == data.errorno){
					//显示图片
					var image_url = data.data.image_url;
					var html = '<img src="'+image_url+'" />';
					$(".house-image-cons").append(html);
				}else{
					alert(data.errormsg);	
				}
			}
			});	
	}); 
	

})
