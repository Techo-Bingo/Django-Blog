<!DOCTYPE html>
<html>
	<head>
		<style type="text/css">
			body {
			    font-family: arial;
			  }
			  table {
			    border: 1px solid #ccc;
			    width: 100%;
			    margin:0;
			    padding:0;
			    border-collapse: collapse;
			    border-spacing: 0;
				table-layout:fixed;/* 只有定义了表格的布局算法为fixed，下面td的定义才能起作用。 */
			  }
			  
			th {
				background-color:#666666
			}
			
			  table tr {
			    border: 1px solid #ddd;
			    padding: 5px;
			  }
			
			  table th, table td {
			    padding: 10px;
			    text-align: center;
				border: 1px solid #ddd;
			  }

			  table th {
			    /*text-transform: uppercase;*/
			    font-size: 19px;
			    letter-spacing: 1px;
			  }

			  @media screen and (max-width: 600px) {

			    table {
			      border: 0;
			    }

			    table thead {
			      display: none;
			    }

			    table tr {
			      margin-bottom: 10px;
			      display: block;
			      border-bottom: 2px solid #bbb;
			    }

			    table td {
			      display: block;
			      text-align: right;
			      font-size: 13px;
			      border-bottom: 1px dotted #bbb;
			    }

			    table td:last-child {
			      border-bottom: 0;
			    }

			    table td:before {
			      content: attr(data-label);
			      float: left;
			      text-transform: uppercase;
			      font-weight: bold;
			    }
			  }
			/* 自动隔行颜色加深效果 */  
			tbody tr:nth-child(odd) { 
				background: #eee;
			}
			/* 鼠标选中效果 */
			tbody tr:hover td
			{
				background: #CCCCCC;
			}
		</style>

	</head>
	<body>
		<table>
		<thead>
		<tr>
		<th>序号</th>
		<th>标题</th>
		<th>时间</th>
		<!--td>文章</td-->
		</tr>
		</thead>
		{% for p in posts %}
		<tbody>
		<tr>
			<td data-label="序号">{{p.slug}}</td>
			<td data-label="标题">{{p.title}}</td>
			<td data-label="时间">{{p.pub_date}}</td>
			<!--td>{{p.body}}</td-->
		</tr>
		</tbody>
	{% endfor %}
	</table>
	</body>
</html>

