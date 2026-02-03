# API接口文档

## 智能姓名生成服务 API 文档

**版本**: 2.0.1
**基础URL**: `http://localhost:8000/api/v1`
**认证方式**: JWT Bearer Token

## 目录

1. [认证接口](#认证接口)
2. [用户管理接口](#用户管理接口)
3. [姓名生成接口](#姓名生成接口)
4. [收藏管理接口](#收藏管理接口)
5. [企业起名管理接口](#企业起名管理接口)
6. [产品起名管理接口](#产品起名管理接口)
7. [数据模型](#数据模型)
8. [错误处理](#错误处理)

## 认证接口

### 1. 获取邮箱验证码

**接口地址**: `GET /auth/code`

**描述**: 发送邮箱验证码用于用户注册

**请求参数**:
```json
{
  "email": "user@example.com"
}
```

**响应示例**:
```json
{
  "result": "success"
}
```

### 2. 用户注册

**接口地址**: `POST /auth/register`

**描述**: 使用邮箱验证码完成用户注册

**请求体**:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123",
  "confirm_password": "password123",
  "code": "1234"
}
```

**响应示例**:
```json
{
  "result": "success"
}
```

### 3. 用户登录

**接口地址**: `POST /auth/login`

**描述**: 用户账号登录

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "nickname": "testuser",
    "gender": "未知",
    "avatar": "",
    "avatar_url": "",
    "phone": ""
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. 用户登出

**接口地址**: `POST /auth/logout`

**描述**: 用户安全登出

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "result": "success"
}
```

## 用户管理接口

### 1. 获取用户资料

**接口地址**: `GET /user/profile`

**描述**: 获取当前用户的完整资料信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "nickname": "张三",
  "gender": "男",
  "avatar": "avatar_1_xxx.png",
  "phone": "13800138000"
}
```

### 2. 更新用户资料

**接口地址**: `PUT /user/profile`

**描述**: 更新用户的个人信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "nickname": "张三",
  "gender": "男",
  "phone": "13800138000"
}
```

**响应示例**:
```json
{
  "result": "success",
  "message": "资料更新成功"
}
```

### 3. 上传头像

**接口地址**: `POST /user/avatar`

**描述**: 上传用户头像图片

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**请求体**: FormData
- `file`: 图片文件 (支持 jpg, png, jpeg, gif 格式，最大5MB)

**响应示例**:
```json
{
  "avatar_url": "http://127.0.0.1:8000/static/avatars/avatar_1_xxx.png",
  "message": "头像上传成功"
}
```

### 4. 用户注销

**接口地址**: `POST /user/deleteuser`

**描述**: 永久删除用户账号及所有相关数据

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "result": "success",
  "message": "用户已永久注销"
}
```

### 5. 修改密码

**接口地址**: `PUT /user/change-password`

**描述**: 修改用户登录密码

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**响应示例**:
```json
{
  "message": "密码修改成功"
}
```

## 姓名生成接口

### 1. 生成个人姓名

**接口地址**: `POST /name`

**描述**: 使用AI生成符合条件的个人姓名

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "surname": "张",
  "gender": "男",
  "length": "两字",
  "other": "希望名字有文化底蕴",
  "exclude": ["狗", "猪"]
}
```

**响应示例**:
```json
{
  "names": [
    {
      "name": "张文博",
      "reason": "文博代表有文化、有学识，符合您的要求"
    },
    {
      "name": "张宇航",
      "reason": "宇航寓意前程远大，志向高远"
    }
  ]
}
```

### 2. 生成企业名称

**接口地址**: `POST /name/company`

**描述**: 根据行业和定位生成企业名称

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "industry": "科技",
  "company_type": "有限公司",
  "business_scope": "人工智能研发",
  "positioning": "高端",
  "length": "3字",
  "style": "现代",
  "exclude": ["垃圾", "废物"]
}
```

**响应示例**:
```json
{
  "names": [
    {
      "name": "智创科技有限公司",
      "reason": "体现科技创新，符合现代科技企业形象"
    },
    {
      "name": "睿思人工智能有限公司",
      "reason": "睿思代表智慧思考，符合AI研发定位"
    }
  ]
}
```

### 3. 生成产品名称

**接口地址**: `POST /name/product`

**描述**: 根据产品特点生成产品名称

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "product_type": "APP",
  "product_function": "在线学习平台",
  "target_audience": "学生",
  "market_positioning": "高端",
  "length": "2字",
  "style": "简洁",
  "exclude": ["垃圾", "坑"]
}
```

**响应示例**:
```json
{
  "names": [
    {
      "name": "学优",
      "reason": "简洁明了，突出学习和优秀"
    },
    {
      "name": "智学",
      "reason": "体现智慧学习，符合在线教育定位"
    }
  ]
}
```

### 4. 姓名测评

**接口地址**: `POST /name/evaluate`

**描述**: 对指定姓名进行多维度测评

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "full_name": "张三",
  "gender": "男",
  "birthdate": "2000-01-01"
}
```

**响应示例**:
```json
{
  "name": "张三",
  "score": 85,
  "evaluation": {
    "overall": "这个名字整体不错，具有一定的文化内涵和美感",
    "advantage": [
      "笔画搭配和谐",
      "读音响亮上口",
      "寓意积极向上"
    ],
    "disadvantage": [
      "相对较为常见",
      "辨识度一般"
    ],
    "suggestion": "建议可以考虑一些更有特色的字来增强个性"
  }
}
```

### 5. 获取姓名历史记录

**接口地址**: `GET /name/history`

**描述**: 分页获取用户的姓名生成历史

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
[
  {
    "id": 1,
    "input_params": {
      "surname": "张",
      "gender": "男",
      "length": "两字"
    },
    "generated_names": {
      "names": [
        {"name": "张文博", "reason": "有文化底蕴"},
        {"name": "张宇航", "reason": "寓意远大"}
      ]
    },
    "model_used": "load_balanced",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### 6. 批量删除历史记录

**接口地址**: `DELETE /name/history/batch`

**描述**: 批量删除指定的历史记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "deleted_count": 3
}
```

### 7. 获取姓名重复度查询

**接口地址**: `GET /name/repetition`

**描述**: 查询指定姓名在数据库中的重复度

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `name`: 姓名 (必填)
- `gender`: 性别 (必填，男/女)
- `region`: 地区 (可选)

**响应示例**:
```json
{
  "name": "张三",
  "gender": "男",
  "region": "全国",
  "total_count": 1250,
  "repetition_rate": 0.08,
  "rank": 156,
  "analysis": "这个名字相对常见，在同性别中排名第156位"
}
```

### 8. 获取热门姓名排行

**接口地址**: `GET /name/top`

**描述**: 获取使用次数最多的姓名排行榜

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `gender`: 性别筛选 (可选，男/女)
- `limit`: 返回数量 (默认: 10, 最大: 50)

**响应示例**:
```json
[
  {
    "name": "张伟",
    "gender": "男",
    "count": 156,
    "percentage": 2.34
  },
  {
    "name": "李娜",
    "gender": "女",
    "count": 142,
    "percentage": 2.13
  }
]
```

## 收藏管理接口

系统支持三种类型的起名收藏：个人姓名、企业名称、产品名称。每种类型都可以通过通用收藏API或专门的收藏API进行管理。

### 1. 添加收藏（通用）

**接口地址**: `POST /favorite/add`

**描述**: 将任意类型的历史记录添加到收藏（支持个人姓名、企业名称、产品名称）

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "收藏成功",
  "favorite_id": 1
}
```

**支持的记录类型**:
- 个人姓名历史记录ID
- 企业起名历史记录ID
- 产品起名历史记录ID

### 2. 取消收藏（通用）

**接口地址**: `POST /favorite/remove`

**描述**: 从收藏中移除指定记录（支持所有类型）

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "取消收藏成功"
}
```

### 3. 获取收藏列表（通用）

**接口地址**: `GET /favorite/list`

**描述**: 获取用户的所有收藏记录（包含所有类型）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
{
  "total": 25,
  "items": [
    {
      "id": 1,
      "history_id": 123,
      "type": "name",
      "created_at": "2024-01-01T10:00:00Z",
      "history_info": {
        "input_params": {
          "surname": "张",
          "gender": "男",
          "length": "两字"
        },
        "generated_names": {...}
      }
    },
    {
      "id": 2,
      "history_id": 456,
      "type": "company",
      "created_at": "2024-01-02T10:00:00Z",
      "history_info": {
        "industry": "科技",
        "company_type": "有限公司",
        "generated_names": {...}
      }
    },
    {
      "id": 3,
      "history_id": 789,
      "type": "product",
      "created_at": "2024-01-03T10:00:00Z",
      "history_info": {
        "product_type": "APP",
        "product_function": "在线学习",
        "generated_names": {...}
      }
    }
  ]
}
```

## 企业起名管理接口

### 1. 获取企业起名历史

**接口地址**: `GET /name/company/history`

**描述**: 分页获取企业起名历史记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
[
  {
    "id": 1,
    "industry": "科技",
    "company_type": "有限责任公司",
    "business_scope": "软件开发和技术服务",
    "positioning": "创新型科技企业",
    "length": "4字",
    "style": "现代简约",
    "exclude": ["测试", "临时"],
    "generated_names": {...},
    "model_used": "deepseek-company",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### 2. 删除企业起名历史

**接口地址**: `DELETE /name/company/history/{history_id}`

**描述**: 删除指定的企业起名历史记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `history_id`: 历史记录ID

### 3. 添加企业起名收藏

**接口地址**: `POST /name/company/favorite/add`

**描述**: 将企业起名历史记录添加到收藏

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**请求示例**:
```bash
POST /api/v1/name/company/favorite/add
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "收藏成功"
}
```

### 4. 移除企业起名收藏

**接口地址**: `POST /name/company/favorite/remove`

**描述**: 从收藏中移除企业起名记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**请求示例**:
```bash
POST /api/v1/name/company/favorite/remove
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "取消收藏成功"
}
```

### 5. 获取企业起名收藏列表

**接口地址**: `GET /name/company/favorite/list`

**描述**: 获取企业起名收藏列表

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
[
  {
    "id": 1,
    "history_id": 123,
    "created_at": "2024-01-01T10:00:00Z",
    "history_info": {
      "industry": "科技",
      "company_type": "有限公司",
      "business_scope": "AI研发",
      "generated_names": {...}
    }
  }
]
```

## 产品起名管理接口

### 1. 获取产品起名历史

**接口地址**: `GET /name/product/history`

**描述**: 分页获取产品起名历史记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
[
  {
    "id": 1,
    "product_type": "智能手机",
    "product_function": "高端智能手机，注重拍照和性能",
    "target_audience": "年轻人",
    "market_positioning": "高端旗舰",
    "length": "2字",
    "style": "现代时尚",
    "exclude": ["测试"],
    "generated_names": {...},
    "model_used": "deepseek-product",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### 2. 删除产品起名历史

**接口地址**: `DELETE /name/product/history/{history_id}`

**描述**: 删除指定的产品起名历史记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `history_id`: 历史记录ID

### 3. 添加产品起名收藏

**接口地址**: `POST /name/product/favorite/add`

**描述**: 将产品起名历史记录添加到收藏

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**请求示例**:
```bash
POST /api/v1/name/product/favorite/add
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "收藏成功"
}
```

### 4. 移除产品起名收藏

**接口地址**: `POST /name/product/favorite/remove`

**描述**: 从收藏中移除产品起名记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "history_id": 1
}
```

**请求示例**:
```bash
POST /api/v1/name/product/favorite/remove
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "history_id": 1
}
```

**响应示例**:
```json
{
  "message": "取消收藏成功"
}
```

### 5. 获取产品起名收藏列表

**接口地址**: `GET /name/product/favorite/list`

**描述**: 获取产品起名收藏列表

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)

**响应示例**:
```json
[
  {
    "id": 1,
    "history_id": 456,
    "created_at": "2024-01-01T10:00:00Z",
    "history_info": {
      "product_type": "APP",
      "product_function": "在线学习平台",
      "target_audience": "学生",
      "generated_names": {...}
    }
  }
]
```

## 数据模型

### 用户相关模型

#### RegisterIn (注册请求)
```python
{
  "email": "user@example.com",      # 邮箱
  "username": "testuser",          # 用户名 (3-20字符)
  "password": "password123",       # 密码 (6-20字符)
  "confirm_password": "password123", # 确认密码
  "code": "1234"                   # 邮箱验证码 (4位数字)
}
```

#### UserProfileResponse (用户资料响应)
```python
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "nickname": "张三",
  "gender": "男",                  # 男/女/未知
  "avatar": "avatar_1_xxx.png",    # 头像文件名
  "phone": "13800138000"           # 手机号
}
```

### 姓名生成相关模型

#### NameIn (姓名生成请求)
```python
{
  "surname": "张",                 # 姓氏
  "gender": "男",                  # 性别: 不限/男/女
  "length": "两字",                # 字数: 不限/单字/两字
  "other": "希望有文化底蕴",       # 其他要求
  "exclude": ["狗", "猪"]          # 排除的字词
}
```

#### NameOut (姓名生成响应)
```python
{
  "names": [
    {
      "name": "张文博",            # 生成的姓名
      "reason": "有文化底蕴"       # 推荐理由
    }
  ]
}
```

#### CompanyNameIn (企业起名请求)
```python
{
  "industry": "科技",              # 所属行业
  "company_type": "有限公司",      # 企业类型
  "business_scope": "AI研发",      # 经营范围
  "positioning": "高端",           # 市场定位
  "length": "3字",                 # 名称字数
  "style": "现代",                 # 风格偏好
  "exclude": ["垃圾"]              # 排除字词
}
```

#### ProductNameIn (产品起名请求)
```python
{
  "product_type": "APP",           # 产品类型
  "product_function": "在线学习",  # 产品功能
  "target_audience": "学生",       # 目标用户
  "market_positioning": "高端",    # 市场定位
  "length": "2字",                 # 名称字数
  "style": "简洁",                 # 风格偏好
  "exclude": ["坑"]                # 排除字词
}
```

#### NameEvaluateIn (姓名测评请求)
```python
{
  "full_name": "张三",             # 完整姓名
  "gender": "男",                  # 性别
  "birthdate": "2000-01-01"        # 出生日期 (可选)
}
```

#### NameEvaluateOut (姓名测评响应)
```python
{
  "name": "张三",
  "score": 85,                     # 综合评分 (0-100)
  "evaluation": {
    "overall": "整体评价",          # 总体评价
    "advantage": ["优点1", "优点2"], # 优点列表
    "disadvantage": ["缺点1"],      # 缺点列表
    "suggestion": "改进建议"        # 建议
  }
}
```

## 错误处理

### HTTP状态码

- `200`: 成功
- `201`: 创建成功
- `204`: 无内容 (删除成功)
- `400`: 请求参数错误
- `401`: 未授权 (需要登录)
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突
- `422`: 数据验证失败
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "error": {
    "code": 400,
    "message": "请求参数错误",
    "type": "validation_error",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  }
}
```

### 常见错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式和必填字段 |
| 401 | 身份验证失败 | 检查token是否有效或重新登录 |
| 403 | 权限不足 | 确认用户权限或联系管理员 |
| 404 | 资源不存在 | 检查资源ID是否正确 |
| 409 | 资源冲突 | 资源已存在或状态冲突 |
| 422 | 数据验证失败 | 根据错误详情修正数据格式 |
| 500 | 服务器错误 | 稍后重试或联系技术支持 |

### AI服务相关错误

```json
{
  "error": {
    "code": 503,
    "message": "AI服务暂时不可用",
    "type": "ai_service_error",
    "details": {
      "service": "deepseek",
      "retry_after": 30
    }
  }
}
```

## 使用说明

### 1. 认证流程

1. 调用 `/auth/code` 获取验证码
2. 使用验证码调用 `/auth/register` 完成注册
3. 调用 `/auth/login` 获取访问令牌
4. 在后续请求中使用 `Authorization: Bearer <token>` 头

### 2. 分页查询

大部分列表接口支持分页：

```javascript
// 获取第2页，每页20条记录
GET /api/v1/name/history?page=2&page_size=20
```

### 3. 文件上传

头像上传使用 `multipart/form-data` 格式：

```javascript
const formData = new FormData();
formData.append('file', imageFile);

fetch('/api/v1/user/avatar', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### 4. 错误处理

客户端应始终检查响应状态码和错误信息：

```javascript
try {
  const response = await fetch('/api/v1/name', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(requestData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }

  const result = await response.json();
  // 处理成功响应
} catch (error) {
  // 处理错误
  console.error('API请求失败:', error.message);
}
```

### 5. 收藏功能说明

系统提供统一的收藏功能，支持三种类型的起名记录：

**统一使用孩子收藏API处理所有收藏类型：**

- **孩子起名收藏**: `POST /api/v1/favorite/add`
- **企业起名收藏**: `POST /api/v1/favorite/add` (使用不同的history_id)
- **产品起名收藏**: `POST /api/v1/favorite/add` (使用不同的history_id)

所有收藏API都使用统一的JSON请求体格式：

```json
{
  "history_id": 1
}
```

收藏列表API返回包含所有类型收藏的统一结果：

```json
{
  "total": 25,
  "items": [
    {
      "id": 1,
      "history_id": 123,
      "type": "name",
      "created_at": "2024-01-01T10:00:00Z",
      "history_info": {...}
    },
    {
      "id": 2,
      "history_id": 456,
      "type": "company",
      "created_at": "2024-01-02T10:00:00Z",
      "history_info": {...}
    }
  ]
}
```

## 版本历史

- **v2.0.1** (2025-01-XX)
  - ✅ 统一收藏API架构，解决多进程冲突导致的404错误
  - 🔧 重构收藏仓库，实现多类型历史记录自动识别
  - 🎯 简化前端集成，统一使用 `/api/v1/favorite/*` 系列API
  - 📊 增强收藏列表API，支持类型标识和排序
  - 🛠️ 优化错误处理，完善ResponseValidationError处理机制
  - 📚 更新文档，完善收藏功能说明和类型区分指南

- **v2.0.2** (2024-12-XX)
  - 🔄 统一收藏API设计，所有收藏接口都使用JSON请求体格式
  - 🎯 简化企业起名和产品起名收藏API，与孩子起名收藏保持一致
  - 📚 更新API文档，完善收藏功能说明和使用示例
  - 🧪 优化测试文档，提供统一的API调用格式

- **v2.0.1** (2024-12-XX)
  - 🐛 修复企业起名和产品起名收藏功能
  - 🔧 优化通用收藏API，支持所有三种类型的起名记录
  - 📚 更新API文档，完善收藏管理接口说明
  - 🧪 增强测试文档，添加企业起名和产品起名收藏测试用例

- **v2.0.0** (2024-01-XX)
  - 重构API架构，支持多场景命名
  - 添加企业起名和产品起名功能
  - 优化AI服务负载均衡
  - 增强用户体验和错误处理

- **v1.0.0** (2024-01-XX)
  - 基础的个人姓名生成功能
  - 用户认证和资料管理
  - 历史记录和收藏功能
