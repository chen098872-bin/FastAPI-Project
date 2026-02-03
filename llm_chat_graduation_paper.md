毕 业 论 文（设计）


基于FastAPI的智能多场景命名系统









教务处  制


摘    要

随着人工智能技术的快速发展，大语言模型在自然语言处理领域展现出强大的能力，为各行业智能化转型提供了新的机遇。智能命名作为语言生成的重要应用场景，在个人、企业和产品命名中具有重要价值。本系统基于FastAPI框架开发，集成DeepSeek和Alibaba AI等多家大语言模型服务，提供个人姓名、企业名称和产品名称的智能生成服务。系统采用分层架构设计与模块化编程，通过SQLAlchemy实现数据持久层与MySQL数据库的集成，构建面向多场景的智能命名服务平台。

系统以用户为中心，深度融合AI技术与命名需求，重点围绕个人姓名生成、企业名称生成、产品名称生成等方向展开设计，并在AI服务集成方面，实现多模型负载均衡与智能切换，支持跨服务的高可用命名服务。系统通过JWT认证确保用户数据安全，采用异步处理提升并发性能，为用户提供高效、准确的命名服务。

本文研究当前AI技术发展现状和智能命名的应用价值，通过了解国内外智能命名系统建设现状，调研用户命名需求的关键点，对智能多场景命名系统软件建设的全部生命周期，分别进行了详细的论述。

关键词：人工智能；大语言模型；FastAPI；智能命名；异步处理

Abstract

With the rapid development of artificial intelligence technology, large language models have demonstrated powerful capabilities in the field of natural language processing, providing new opportunities for intelligent transformation across industries. Intelligent naming, as an important application scenario of language generation, holds significant value in personal, corporate, and product naming. This system is developed based on the FastAPI framework, integrating multiple large language model services such as DeepSeek and Alibaba AI, providing intelligent generation services for personal names, company names, and product names. The system adopts a layered architecture design and modular programming, integrating the data persistence layer with MySQL database through SQLAlchemy, building an intelligent naming service platform for multiple scenarios.

Taking users as the center, the system deeply integrates AI technology with naming requirements, focusing on personal name generation, company name generation, product name generation and other directions, and in terms of AI service integration, achieves multi-model load balancing and intelligent switching, supporting cross-service high-availability naming services. The system ensures user data security through JWT authentication and improves concurrent performance through asynchronous processing, providing users with efficient and accurate naming services.

This study examines the current status of AI technology development and the application value of intelligent naming. By understanding the construction status of domestic and international intelligent naming systems and investigating the key points of user naming needs, it provides a detailed discussion of the entire lifecycle of intelligent multi-scenario naming system software development.

Keywords: Artificial Intelligence; Large Language Models; FastAPI; Intelligent Naming; Asynchronous Processing


目    录

摘    要	I
Abstract	II
目    录	III
第一章 绪 论

1.1课题背景与意义

随着人工智能技术的迅猛发展，大语言模型（Large Language Models）在自然语言处理领域展现出革命性的能力，从简单的文本生成到复杂的推理任务，都取得了突破性进展。智能命名作为语言生成的重要应用场景，在个人、企业和产品命名中具有不可替代的价值。传统的人工命名方式往往耗时耗力，难以兼顾创意性、文化内涵和市场适应性等问题，而基于AI的智能命名技术能够快速生成符合用户需求的优质名称，大大提升命名效率。

本研究以人工智能技术为驱动，构建基于FastAPI的智能多场景命名系统，通过集成DeepSeek、Alibaba AI等先进大语言模型，实现个人姓名、企业名称和产品名称的智能生成。系统采用异步处理架构，支持高并发访问，确保用户获得流畅的命名体验。同时，通过精细化的用户认证和数据安全机制，保护用户隐私和系统安全。该系统不仅为用户提供便捷的命名服务，更通过历史记录管理和收藏功能，帮助用户追踪和复用优秀的命名结果，为人工智能在创意领域的应用提供了新的实践范例。

在社会价值层面，智能命名系统能够降低创业门槛，为中小企业提供专业的名称咨询服务；在技术价值层面，该系统展示了现代Web框架、AI集成、异步编程等技术的综合应用，为相关领域的研究和开发提供了参考。

1.2课题研究现状

1.2.1国内课题研究现状

国内智能命名技术的研究起步较晚，但发展迅速。随着人工智能浪潮的兴起，越来越多的企业和研究机构开始关注AI在创意领域的应用。百度、腾讯、阿里巴巴等互联网巨头纷纷推出AI命名服务，如百度的"文心一言"命名功能、阿里的"通义千问"在品牌命名方面的应用。清华大学、北京大学等高校也在AI创意生成领域开展深入研究，取得了丰硕成果。

在智能命名应用层面，"红海市场"中的企业命名服务已相对成熟，新兴领域如宠物命名、游戏角色命名等也在快速发展。2023年，中国AI产业规模突破5000亿元，其中自然语言处理相关应用占比超过30%。多家创业公司专注于细分领域的AI命名服务，如专注于企业命名的"起名宝"、专注于产品命名的"名创客"等平台。

国内研究重点关注AI模型的中文语境适应性、文化内涵理解和商业价值实现。清华大学的研究显示，基于中文语料训练的AI模型在成语理解、诗词创作方面已达到人类水平；在命名领域，中科院的研究团队开发了专门的品牌命名评估模型，能够从商业价值、文化内涵、记忆度等多个维度评估名称质量。

当前国内智能命名系统主要面临模型泛化能力不足、文化理解不深、创意重复度高等挑战。国家自然科学基金委将AI创意生成列为重点资助方向，鼓励跨学科研究，推动AI技术在文化创意产业的应用。

1.2.2国外课题研究现状

国外智能命名技术研究起步更早，技术积累更为深厚。OpenAI的GPT系列模型在创意生成领域表现出色，其命名功能已被广泛应用于品牌咨询、产品设计等领域。Google的Bard（现为Gemini）也在命名生成方面展现了强大的能力，能够根据用户描述生成具有创意性和实用性的名称。

学术研究方面，斯坦福大学、麻省理工学院等顶尖高校在AI创意生成领域开展了长期研究。斯坦福的Creative AI实验室专注于AI在艺术、设计领域的应用，开发了多个创意生成工具。MIT媒体实验室的研究显示，AI生成的创意内容在某些领域已超过人类水平。

在商业应用层面，国外涌现出众多专业的AI命名平台。Namelix、Brandmark等工具通过集成多种AI模型，提供从名称生成到Logo设计的完整服务。Adobe的Sensei AI平台将AI创意生成融入设计工作流，帮助设计师快速生成命名灵感。

国外研究领先于国内的主要优势体现在：数据规模更大、模型参数更多、算法优化更成熟。2023年，OpenAI的GPT-4模型参数达到万亿级别，在命名生成任务上的表现令人印象深刻。但也存在文化偏见、创意同质化等问题。当前国际研究正从单一模型向多模型融合、从通用生成向专业领域定制转变。

1.3论文研究内容

主要研究基于FastAPI的智能多场景命名系统，构建面向个人、企业和产品的AI命名服务平台。集成DeepSeek和Alibaba AI等多模型服务，提供个人姓名、企业名称、产品名称的智能生成。建立用户认证体系，确保数据安全；实现历史记录和收藏功能，便于用户管理命名结果；采用异步处理架构，提升系统并发性能。

在技术实现方面，采用FastAPI框架构建高性能API服务，通过SQLAlchemy实现数据持久化，集成LangChain框架实现AI模型调用和负载均衡。系统支持多场景命名需求，包括基于生辰八字的个人姓名生成、基于行业特性的企业名称生成、基于产品功能的命名生成等。

架构设计采用分层架构模式，包括表现层、业务逻辑层、数据访问层和外部服务层。前端通过RESTful API与后端交互，后端负责业务处理和AI服务调用。数据库设计采用关系型数据库MySQL，结合Redis缓存提升访问性能。

安全设计方面，采用JWT无状态认证，bcrypt密码哈希，CORS跨域防护等机制，确保用户数据安全。系统通过异步处理和连接池优化，提升高并发场景下的性能表现。

1.4本章小结

本章主要阐述了智能多场景命名系统的研究背景和意义，分析了国内外相关技术的发展现状，明确了本课题的主要研究内容和技术路线，为后续系统设计与实现奠定了基础。
第二章 系统相关技术

2.1 Python语言介绍

Python作为当前最受欢迎的编程语言之一，以其简洁明了的语法、丰富的生态系统和强大的表达能力，在Web开发、数据科学、人工智能等领域占据主导地位。作为一种解释型语言，Python支持动态类型和自动内存管理，大大降低了开发复杂度。特别是在AI应用开发中，Python凭借NumPy、Pandas、TensorFlow等专业库，成为AI开发的首选语言。

在Web开发领域，Python的Django和Flask框架曾长期主导市场，而近年来新兴的FastAPI框架凭借异步处理能力和自动API文档生成功能，迅速崛起为现代Web框架的代表。Python的异步编程通过asyncio库实现，支持协程和事件循环，能够高效处理高并发场景。同时，Python强大的类型提示功能（Type Hints）为代码的可维护性和IDE支持提供了保障。

2.2 FastAPI框架

FastAPI是基于Python 3.7+开发的现代异步Web框架，专为构建高性能API而设计。它结合了Starlette的异步能力和Pydantic的数据验证特性，提供卓越的开发体验和运行性能。与传统的Django、Flask框架相比，FastAPI具有显著优势：

框架核心特性包括自动API文档生成，支持OpenAPI和JSON Schema标准；基于Pydantic的数据验证和序列化，确保输入数据的类型安全；原生支持异步编程，能够充分利用Python的asyncio特性；依赖注入系统简化组件管理和测试；内置安全功能支持OAuth2、JWT等认证协议。

在性能方面，FastAPI基于Starlette构建，支持异步请求处理，能够轻松应对高并发场景。官方基准测试显示，FastAPI的性能接近Node.js和Go语言框架，是Python Web框架中的佼佼者。特别是在AI应用场景中，FastAPI的异步特性能够有效处理耗时的AI模型调用，提升整体响应速度。

2.3 SQLAlchemy技术

SQLAlchemy是Python最强大的ORM（对象关系映射）框架之一，提供灵活、高效的数据库操作接口。它支持多种数据库后端，包括MySQL、PostgreSQL、SQLite等，通过统一的API实现跨数据库的兼容性。SQLAlchemy采用双层架构设计：Core层提供SQL表达式语言和数据库连接池，ORM层则提供对象映射和查询接口。

核心特性包括：强大的查询构造器，支持复杂SQL查询的Python化表达；连接池管理，优化数据库连接使用；事务支持，确保数据一致性；延迟加载和预加载，优化查询性能；原生支持异步操作，通过aiomysql、asyncpg等驱动实现。

在智能命名系统中，SQLAlchemy负责用户数据、历史记录、收藏数据的持久化存储。通过ORM映射，将Python对象与数据库表建立关联，简化了CRUD操作。同时，结合Alembic迁移工具，实现数据库结构的版本控制和自动化升级。

2.4 大语言模型集成

系统集成了DeepSeek和Alibaba AI两家大语言模型服务，通过LangChain框架实现统一调用和管理。LangChain是一个专为大语言模型应用开发设计的框架，提供模型抽象、提示工程、链式调用等核心功能。它支持多种LLM提供商的API统一接入，简化了多模型集成的复杂度。

DeepSeek是由中科院计算所开发的开源大语言模型，在中文理解和生成方面表现出色。Alibaba AI（通义千问）则具备强大的多语言能力和行业知识。系统通过智能负载均衡器，根据模型可用性、响应速度和生成质量等因素，动态选择最优的AI服务。

在命名生成场景中，不同的AI模型具有各自优势：DeepSeek在中文文化内涵理解方面更擅长，适合生成富有诗意的名称；Alibaba AI在商业逻辑推理方面更强，适合生成具有市场价值的名称。通过多模型集成和切换机制，系统能够为用户提供更优质的命名服务。

2.5 JWT认证技术

JWT（JSON Web Token）是一种开放标准（RFC 7519），用于在各方之间安全地传输信息。它采用JSON格式定义令牌结构，通过数字签名确保信息完整性。JWT令牌包含Header、Payload和Signature三个部分，通过Base64编码传输。

系统采用JWT实现无状态认证，避免了传统Session机制的服务器存储开销。用户登录后，服务器生成包含用户ID、过期时间等信息的JWT令牌，返回给客户端。客户端在后续请求中携带该令牌，服务器通过验证签名和过期时间来确认用户身份。

Python的PyJWT库提供完整的JWT实现，支持多种签名算法。结合bcrypt密码哈希算法，系统实现了安全可靠的用户认证体系。同时，通过Redis缓存JWT黑名单，支持令牌主动失效功能，提升了安全性。
第三章 系统分析

3.1系统需求描述

3.1.1系统业务建模

智能多场景命名系统的主要角色分为普通用户和管理员两个主要角色。普通用户需要注册账户并通过邮箱验证激活，通过登录获取访问令牌。用户可以根据个人需求生成不同类型的名称，包括个人姓名、企业名称和产品名称。用户可以将满意的命名结果加入收藏，便于后续查看和管理。同时，系统记录用户的命名历史，帮助用户追踪使用情况。模型如图3.1所示

图3.1 用户需求用例图

管理员主要负责系统运维和数据管理，包括查看用户统计信息、监控系统运行状态、管理AI服务配置等。管理员可以查看系统的使用情况报告，包括用户活跃度、命名类型分布、AI服务调用统计等。模型如图3.2所示

图3.2 管理员需求用例图

3.1.2系统需求分析

用户功能需求：
(1) 用户注册与登录：支持邮箱注册、密码登录、邮箱验证码验证
(2) 个人信息管理：支持修改昵称、头像、联系方式等个人信息
(3) 个人姓名生成：基于姓氏、性别、长度偏好等参数生成个性化姓名
(4) 企业名称生成：基于行业、公司类型、经营范围等参数生成企业名称
(5) 产品名称生成：基于产品类型、功能特点、目标受众等参数生成产品名称
(6) 收藏管理：支持收藏/取消收藏各种类型的命名结果
(7) 历史记录：查看个人的命名历史，包括生成时间、参数、结果等
(8) 使用统计：查看个人使用情况统计

管理员功能需求：
(1) 用户管理：查看用户列表、用户统计信息
(2) 系统监控：查看系统运行状态、API调用统计
(3) AI服务管理：配置AI模型参数、监控服务可用性
(4) 数据管理：查看和导出系统数据统计

系统功能需求：
(1) 多AI模型集成：支持DeepSeek、Alibaba AI等多模型调用
(2) 智能负载均衡：根据模型性能和可用性自动切换
(3) 异步处理：支持高并发请求处理
(4) 数据持久化：用户数据、历史记录、收藏数据的安全存储
(5) 安全认证：JWT令牌认证、密码加密存储
(6) 错误处理：完善的异常处理和错误提示机制

3.2系统流程分析

3.2.1开发流程分析

智能多场景命名系统的开发流程采用敏捷开发模式，首先进行需求分析和系统设计，然后分模块实现和测试。开发流程包括以下阶段：

1. 需求分析阶段：明确用户需求，分析业务流程，确定功能范围
2. 技术选型阶段：选择FastAPI、SQLAlchemy等核心技术，确定AI服务集成方案
3. 系统设计阶段：设计系统架构、数据库模型、API接口
4. 编码实现阶段：按模块实现用户认证、命名生成、收藏管理等功能
5. 测试验证阶段：进行单元测试、集成测试、性能测试
6. 部署上线阶段：配置生产环境，部署应用服务

整个开发流程采用版本控制，通过Git管理代码变更。数据库迁移采用Alembic工具，确保数据结构的一致性。

3.2.2功能流程分析

用户注册登录流程：用户在注册页面填写邮箱、密码等信息，系统发送验证码邮件。用户输入验证码完成注册。登录时输入邮箱密码，系统验证通过后返回JWT令牌。如图3.3所示

图3.3 用户注册登录流程图

命名生成流程：用户选择命名类型，填写相关参数。系统根据参数构建AI提示词，调用相应的AI服务生成名称。生成结果经过过滤和排序后返回给用户。如图3.4所示

图3.4 命名生成流程图

收藏管理流程：用户在查看命名结果时，可以选择收藏。系统检查是否已收藏，如果未收藏则添加到收藏列表。用户可以在收藏页面查看、取消收藏。如图3.5所示

图3.5 收藏管理流程图

3.3系统非功能分析

智能多场景命名系统的非功能需求主要包括性能、安全性、可用性、可维护性等方面：

性能需求：
- API响应时间：普通接口<500ms，AI生成接口<10s
- 并发处理能力：支持至少100个并发用户
- 系统可用性：99.9%的正常运行时间

安全性需求：
- 用户认证：采用JWT无状态认证，密码bcrypt哈希
- 数据传输：HTTPS加密传输
- 输入验证：严格的参数验证，防止注入攻击
- 访问控制：基于角色的权限控制

可用性需求：
- 用户界面：简洁直观的操作界面
- 错误处理：友好的错误提示信息
- 多语言支持：支持中英文界面
- 响应式设计：适配不同设备屏幕

可维护性需求：
- 代码规范：遵循PEP8编码规范
- 模块化设计：高内聚、低耦合的模块结构
- 日志记录：完善的日志系统便于问题排查
- 文档完善：详细的API文档和代码注释

扩展性需求：
- 微服务架构：预留扩展接口，支持功能模块拆分
- AI模型扩展：易于集成新的AI服务提供商
- 数据存储扩展：支持多种数据库和缓存方案

3.4本章小结

本章对智能多场景命名系统进行了全面的需求分析，通过用例图展示了系统的功能模块。又详细分析了系统开发流程和核心业务流程，最后从性能、安全性、可用性等多个维度阐述了系统的非功能需求。
第四章 系统设计

4.1系统整体设计

4.1.1系统结构设计

智能多场景命名系统采用分层架构设计，将系统分为四个层次：表现层、业务逻辑层、数据访问层和外部服务层。各层次职责明确，接口清晰，便于开发、测试和维护。

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation Layer)              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  RESTful API 接口                                       │ │
│  │  ├── 用户认证接口 (/auth)                               │ │
│  │  ├── 命名生成接口 (/name)                               │ │
│  │  ├── 收藏管理接口 (/favorite)                           │ │
│  │  └── 用户管理接口 (/user)                               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                  业务逻辑层 (Business Logic Layer)           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ├── 用户认证服务                                        │ │
│  │  ├── AI服务集成                                          │ │
│  │  ├── 负载均衡器                                          │ │
│  │  ├── 收藏管理服务                                        │ │
│  │  └── 数据验证服务                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │   数据访问层 (Data Access Layer) │
          ├───────────────────────┤
          │   ├── 用户仓库          │
          │   ├── 历史记录仓库      │
          │   ├── 收藏仓库          │
          │   └── 统计仓库          │
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │   外部服务层 (External Services) │
          ├─────────────────────────┤
          │   ├── DeepSeek AI     │
          │   ├── Alibaba AI      │
          │   ├── 邮件服务         │
          │   └── Redis缓存        │
          └────────────────────────┘
```

4.1.2系统结构描述

表现层基于FastAPI框架实现RESTful API设计，提供统一的接口规范。所有接口采用JSON格式进行数据交换，支持自动生成OpenAPI规范文档。通过依赖注入机制，实现了控制器与业务逻辑的解耦。

业务逻辑层是系统的核心，负责处理复杂的业务规则和数据转换。该层采用面向对象设计模式，将不同功能模块封装为独立的服务类。通过异步处理机制，提升系统并发性能。核心服务包括：

- 用户认证服务：处理JWT令牌生成、验证和刷新
- AI服务集成：管理多模型调用和负载均衡
- 收藏管理服务：处理收藏的增删改查操作
- 数据验证服务：基于Pydantic进行输入数据验证

数据访问层采用Repository模式，通过SQLAlchemy ORM实现数据持久化。该层抽象了数据库操作细节，为业务逻辑层提供统一的数据访问接口。支持事务管理和连接池优化，确保数据操作的高效性和安全性。

外部服务层集成各类第三方服务，包括AI模型调用、邮件发送、缓存服务等。通过适配器模式封装不同服务的接口差异，提供统一的调用方式。

4.2系统模块设计

系统按功能划分为以下核心模块：

1. **用户认证模块**：负责用户注册、登录、JWT令牌管理
2. **命名生成模块**：实现个人姓名、企业名称、产品名称的AI生成
3. **收藏管理模块**：提供统一的收藏功能，支持多类型记录管理
4. **历史记录模块**：管理用户的命名历史和使用统计
5. **AI服务模块**：集成多AI模型，提供负载均衡和故障转移
6. **系统管理模块**：提供系统监控、配置管理等功能

各模块之间通过依赖注入实现松耦合，模块内部采用高内聚设计。系统支持模块的独立部署和扩展，为未来功能扩展预留了接口。

4.3数据库设计E-R模型

基于系统需求分析，设计了用户、历史记录、收藏等核心实体及其关系。E-R图展示了实体间的关联关系：

```
用户 (User)
├── 1:N ── 姓名历史 (NameHistory)
├── 1:N ── 企业历史 (CompanyNameHistory)
├── 1:N ── 产品历史 (ProductNameHistory)
├── 1:N ── 姓名收藏 (NameFavorite)
├── 1:N ── 企业收藏 (CompanyNameFavorite)
├── 1:N ── 产品收藏 (ProductNameFavorite)
├── 1:N ── 使用统计 (UsageStats)
└── 1:N ── 邮箱验证码 (EmailCode)

历史记录实体包含生成参数、结果、使用的AI模型等信息
收藏实体建立用户与历史记录的多对多关系
```

4.4数据库表设计

系统采用MySQL数据库存储持久化数据，主要表结构如下：

表4.1 用户表 (user)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	email	varchar	100	N	N	邮箱地址，唯一
3	username	varchar	100	N	N	用户名
4	_password	varchar	200	N	N	密码哈希
5	nickname	varchar	100	Y	N	昵称
6	gender	varchar	10	Y	N	性别
7	avatar	text	Y	N	头像路径
8	phone	varchar	11	Y	N	手机号，唯一
9	created_at	datetime	N	N	创建时间
10	updated_at	datetime	N	N	更新时间

表4.2 邮箱验证码表 (email_code)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	email	varchar	100	N	N	邮箱地址
3	code	varchar	10	N	N	验证码
4	created_at	datetime	N	N	创建时间

表4.3 姓名生成历史表 (name_history)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	user_id	int	11	N	N	用户ID，外键
3	input_params	json	N	N	输入参数
4	generated_names	json	N	N	生成结果
5	model_used	varchar	50	N	N	使用的AI模型
6	created_at	datetime	N	N	创建时间

表4.4 企业名称历史表 (company_name_history)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	user_id	int	11	N	N	用户ID，外键
3	industry	varchar	100	N	N	行业
4	company_type	varchar	50	N	N	公司类型
5	business_scope	text	N	N	经营范围
6	positioning	varchar	200	Y	N	定位
7	length	varchar	20	N	N	名称长度
8	style	varchar	50	Y	N	风格
9	exclude	json	Y	N	排除词
10	generated_names	json	N	N	生成结果
11	model_used	varchar	50	N	N	使用的AI模型
12	created_at	datetime	N	N	创建时间

表4.5 产品名称历史表 (product_name_history)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	user_id	int	11	N	N	用户ID，外键
3	product_type	varchar	100	N	N	产品类型
4	product_function	text	N	N	产品功能
5	target_audience	varchar	100	Y	N	目标受众
6	market_positioning	varchar	100	Y	N	市场定位
7	length	varchar	20	N	N	名称长度
8	style	varchar	50	Y	N	风格
9	exclude	json	Y	N	排除词
10	generated_names	json	N	N	生成结果
11	model_used	varchar	50	N	N	使用的AI模型
12	created_at	datetime	N	N	创建时间

表4.6 收藏表 (favorite)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	user_id	int	11	N	N	用户ID，外键
3	record_type	varchar	20	N	N	记录类型
4	record_id	int	11	N	N	记录ID
5	created_at	datetime	N	N	创建时间

表4.7 使用统计表 (usage_stats)
编号	名称	数据类型	长度	允许空值	主键	说明
1	id	int	11	N	Y	主键
2	user_id	int	11	N	N	用户ID，外键
3	action_type	varchar	50	N	N	操作类型
4	action_data	json	Y	N	操作数据
5	created_at	datetime	N	N	创建时间

4.5本章小结

本章介绍了智能多场景命名系统的整体架构设计，通过系统架构图直观展示了各层级间的交互关系。详细阐述了系统的模块划分和数据库设计，包括E-R模型和具体表结构，为后续系统实现提供了完整的蓝图。
第五章 系统实现

5.1系统开发环境介绍

智能多场景命名系统基于Python 3.11开发环境搭建，在系统安全性层面，开发环境配置了虚拟环境隔离机制。开发工具采用PyCharm Professional IDE，支持FastAPI框架的深度集成和调试功能。通过Docker容器化技术，实现开发、测试、生产环境的配置一致性。

具体开发环境配置如下：
- 操作系统：Windows 11 Professional
- Python版本：3.11.5
- IDE：PyCharm 2023.3 Professional
- 数据库：MySQL 8.0.32
- 缓存服务：Redis 7.0
- API测试工具：Postman、HTTPie
- 版本控制：Git 2.40

系统采用分层开发模式，前端通过RESTful API与后端交互，后端基于FastAPI框架实现业务逻辑。数据库迁移采用Alembic工具，确保数据结构版本控制。项目代码通过Black进行格式化，Flake8进行代码质量检查。

5.2系统实现模块

5.2.1用户认证系统

用户认证系统是系统的安全入口，实现了完整的用户生命周期管理。用户注册时需要提供邮箱、密码等基本信息，系统通过smtplib发送验证码邮件进行邮箱验证。登录成功后生成JWT访问令牌和刷新令牌，支持无状态认证。

注册登录页面效果如图5.1所示：

图5.1 用户注册登录界面

核心实现代码包括用户模型定义、认证服务和路由处理：

```python
# 用户模型定义
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    _password = Column(String(200), nullable=False)
    # ... 其他字段

# JWT认证服务
class AuthService:
    @staticmethod
    async def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

# 认证路由
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 注册逻辑实现
    pass
```

5.2.2个人姓名生成

个人姓名生成模块基于AI模型实现智能命名，用户输入姓氏、性别、期望长度等参数，系统调用AI服务生成个性化姓名。支持五行相生、生辰八字等传统文化元素。

姓名生成界面效果如图5.2所示：

图5.2 个人姓名生成界面

核心实现通过LangChain框架封装AI调用：

```python
class NameGenerationAgent:
    def __init__(self, model_client):
        self.model_client = model_client

    async def generate_names(self, params: NameGenerationRequest) -> List[str]:
        prompt = self._build_name_prompt(params)
        response = await self.model_client.generate(prompt)
        return self._parse_names(response)

    def _build_name_prompt(self, params: NameGenerationRequest) -> str:
        return f"""请根据以下要求生成{params.length}个{params.gender}性姓名：
        姓氏：{params.surname}
        风格：{params.style or '现代'}
        要求：{params.requirements or '好听、寓意好'}
        请直接返回姓名列表，不要其他说明。"""
```

5.2.3企业名称生成

企业名称生成模块针对企业用户需求，提供基于行业特征的公司命名服务。用户需要输入行业、公司类型、经营范围等参数，系统生成具有商业价值的企业名称。

企业命名界面效果如图5.3所示：

图5.3 企业名称生成界面

实现代码包括参数验证和AI调用：

```python
@dataclass
class CompanyNameRequest:
    industry: str
    company_type: str
    business_scope: str
    positioning: Optional[str] = None
    length: str = "2-4字"
    style: Optional[str] = None
    exclude: List[str] = field(default_factory=list)

class CompanyNameAgent:
    async def generate_company_names(self, request: CompanyNameRequest) -> List[Dict]:
        prompt = self._build_company_prompt(request)
        ai_response = await self.ai_service.generate(prompt)
        names = self._parse_company_names(ai_response)

        # 过滤排除词
        filtered_names = [
            name for name in names
            if not any(excl in name['name'] for excl in request.exclude)
        ]

        return filtered_names[:10]  # 返回前10个结果
```

5.2.4产品名称生成

产品名称生成模块专注于消费品命名，用户输入产品类型、功能特点、目标受众等信息，系统生成具有市场吸引力的产品名称。

产品命名界面效果如图5.4所示：

图5.4 产品名称生成界面

实现逻辑与企业命名类似，但更注重市场定位和品牌联想：

```python
class ProductNameAgent:
    async def generate_product_names(self, request: ProductNameRequest) -> List[Dict]:
        # 构建产品命名提示词
        prompt = f"""请为以下产品生成创意名称：
        产品类型：{request.product_type}
        主要功能：{request.product_function}
        目标用户：{request.target_audience or '通用'}
        市场定位：{request.market_positioning or '中端市场'}
        名称长度：{request.length}
        风格：{request.style or '现代简约'}

        要求：
        1. 名称要有创意和辨识度
        2. 体现产品特点和价值
        3. 便于记忆和传播
        4. 避免与知名品牌相似

        请生成10个名称，每个名称附带简短理由。"""

        response = await self.ai_service.generate(prompt)
        return self._parse_product_names(response)
```

5.2.5收藏管理系统

收藏管理系统提供统一的收藏功能，支持收藏所有类型的命名结果。用户可以在生成结果页面一键收藏，后续在收藏中心统一管理。

收藏管理界面效果如图5.5所示：

图5.5 收藏管理界面

核心实现采用多态设计，支持不同类型记录的收藏：

```python
class FavoriteService:
    async def add_favorite(self, user_id: int, record_type: str, record_id: int) -> bool:
        # 检查记录是否存在
        if not await self._validate_record(record_type, record_id):
            raise HTTPException(status_code=404, detail="记录不存在")

        # 检查是否已收藏
        existing = await self.favorite_repo.get_favorite(user_id, record_type, record_id)
        if existing:
            return False  # 已收藏

        # 添加收藏
        await self.favorite_repo.add_favorite(user_id, record_type, record_id)
        return True

    async def get_user_favorites(self, user_id: int) -> List[Dict]:
        favorites = await self.favorite_repo.get_user_favorites(user_id)

        # 补充记录详情
        result = []
        for fav in favorites:
            record_data = await self._get_record_data(fav.record_type, fav.record_id)
            if record_data:
                result.append({
                    "id": fav.id,
                    "type": fav.record_type,
                    "data": record_data,
                    "created_at": fav.created_at
                })

        return result
```

5.2.6历史记录管理

历史记录管理模块自动保存用户的命名操作，便于用户回顾和复用。支持按时间、类型等条件筛选历史记录。

历史记录界面效果如图5.6所示：

图5.6 历史记录界面

实现代码包括记录存储和查询功能：

```python
class HistoryService:
    async def save_generation_history(self, user_id: int, generation_type: str,
                                    input_params: Dict, results: List, model_used: str):
        """保存生成历史"""
        history_data = {
            "user_id": user_id,
            "generation_type": generation_type,
            "input_params": input_params,
            "results": results,
            "model_used": model_used,
            "created_at": datetime.utcnow()
        }

        await self.history_repo.save_history(history_data)

        # 更新使用统计
        await self.usage_repo.record_usage(user_id, f"generate_{generation_type}")

    async def get_user_history(self, user_id: int, page: int = 1, limit: int = 20,
                             generation_type: Optional[str] = None) -> Dict:
        """获取用户历史记录"""
        offset = (page - 1) * limit
        histories = await self.history_repo.get_user_history(
            user_id, offset, limit, generation_type
        )

        total = await self.history_repo.get_user_history_count(user_id, generation_type)

        return {
            "items": histories,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
```

5.3本章小结

本章介绍了系统实现所需开发环境及工具，展示了各功能模块的界面效果和核心实现代码。系统采用FastAPI框架实现了高性能的异步API服务，通过SQLAlchemy进行数据持久化，集成多AI模型提供智能命名功能。各模块实现遵循设计原则，具备良好的可维护性和扩展性。
第六章 系统测试

6.1软件测试

在智能多场景命名系统的测试过程中，采用了黑盒测试和白盒测试相结合的方法。黑盒测试主要验证系统功能正确性，用户接口可用性，以及系统在各种输入条件下的响应情况。白盒测试则深入代码逻辑，验证分支覆盖率和错误处理机制。通过自动化测试框架pytest，实现了单元测试、集成测试和端到端测试的全面覆盖。

测试策略包括：
1. 单元测试：针对核心业务逻辑编写测试用例
2. 集成测试：验证模块间的接口调用和数据流转
3. API测试：使用HTTP测试工具验证RESTful接口
4. 性能测试：评估系统在高并发场景下的表现
5. 安全测试：验证认证、授权和数据保护机制

6.2测试环境

测试环境采用与生产环境一致的配置，确保测试结果的可靠性：

- 操作系统：Ubuntu 22.04 LTS
- Python版本：3.11.5
- 数据库：MySQL 8.0.32
- 缓存：Redis 7.0.12
- Web服务器：Uvicorn ASGI服务器
- 测试工具：pytest 7.4.0, httpx 0.24.1
- 负载测试：Locust 2.15.1

测试数据库使用独立的测试实例，避免影响开发数据。API测试通过test_main.http文件进行接口验证。

6.3测试用例及结果分析

6.3.1测试用例设计

表6.1 用户注册测试表
测试目的	操作流程	测试用例	预测结果	测试结果
用户注册	填写注册信息，点击注册按钮	输入有效邮箱和密码	注册成功	注册成功
		输入已存在邮箱	注册失败，提示邮箱已存在	注册失败
		输入无效邮箱格式	注册失败，提示邮箱格式错误	注册失败
		输入弱密码	注册失败，提示密码强度不足	注册失败

表6.2 用户登录测试表
测试目的	操作流程	测试用例	预测结果	测试结果
用户登录	输入邮箱密码，点击登录	输入正确凭据	登录成功，返回JWT令牌	登录成功
		输入错误密码	登录失败，提示密码错误	登录失败
		输入不存在邮箱	登录失败，提示用户不存在	登录失败
		输入空字段	登录失败，提示必填字段为空	登录失败

表6.3 个人姓名生成测试表
测试目的	操作流程	测试用例	预测结果	测试结果
姓名生成	选择参数，点击生成	输入姓氏"张"，性别"男"，长度"两字"	生成10个姓名	生成成功
		输入特殊字符	生成失败，提示参数错误	生成失败
		AI服务不可用	返回错误信息	返回错误信息
		输入超长参数	参数被截断或报错	参数验证通过

表6.4 企业名称生成测试表
测试目的	操作流程	测试用例	预测结果	测试结果
企业命名	填写企业信息，点击生成	行业"科技"，类型"有限公司"，范围"软件开发"	生成10个企业名称	生成成功
		输入空经营范围	生成失败，提示必填字段	生成失败
		包含排除词过滤	结果不包含排除词	过滤生效
		AI响应超时	返回超时错误	返回超时错误

表6.5 收藏管理测试表
测试目的	操作流程	测试用例	预测结果	测试结果
添加收藏	点击收藏按钮	收藏未收藏的记录	收藏成功	收藏成功
		重复收藏同一记录	操作失败，提示已收藏	操作失败
		收藏不存在记录	操作失败，返回404错误	操作失败
		查看收藏列表	显示所有收藏记录	显示正确

表6.6 历史记录测试表
测试目的	操作流程	测试用例	预测结果	测试结果
查看历史	进入历史页面	用户有历史记录	显示历史记录列表	显示正确
		用户无历史记录	显示空列表	显示空列表
		按类型筛选	只显示指定类型记录	筛选正确
		分页查询	正确分页显示记录	分页正确

表6.7 性能测试表
测试目的	操作流程	测试用例	预测结果	测试结果
并发测试	使用Locust模拟并发请求	100并发用户，持续5分钟	响应时间<2秒，成功率>99%	性能达标
		API响应时间测试	单个请求响应时间	<500ms	响应正常
		数据库连接池测试	高并发数据库操作	连接池正常工作	连接池稳定
		内存使用测试	长时间运行内存监控	内存使用稳定	内存稳定

表6.8 安全测试表
测试目的	操作流程	测试用例	预测结果	测试结果
JWT认证	携带令牌访问受保护接口	有效令牌	访问成功	访问成功
		无效令牌	访问失败，返回401	访问失败
		过期令牌	访问失败，返回401	访问失败
SQL注入	在输入字段注入SQL代码	恶意输入	输入被正确转义	安全防护生效
XSS攻击	输入包含脚本的文本	恶意脚本	内容被正确转义	安全防护生效

6.4本章小结

本章对智能多场景命名系统进行了全面的测试验证，涵盖了功能测试、性能测试和安全测试等方面。通过精心设计的测试用例，验证了系统的各项功能正常工作，性能表现良好，安全机制可靠。测试结果表明系统已达到设计要求，可以投入使用。
结    论

本论文围绕基于FastAPI的智能多场景命名系统的设计与实现展开研究，针对传统命名方式效率低下的问题，构建了基于人工智能技术的智能命名服务平台。系统采用FastAPI框架开发，集成DeepSeek和Alibaba AI等多模型服务，提供个人姓名、企业名称和产品名称的智能生成。

系统采用分层架构设计，包括表现层、业务逻辑层、数据访问层和外部服务层。各层职责清晰，接口规范，便于维护和扩展。核心功能包括用户认证、AI命名生成、收藏管理、历史记录等模块。通过JWT认证确保系统安全，异步处理提升并发性能，模块化设计保证了系统的可扩展性。

在技术实现方面，系统集成了LangChain框架实现AI服务调用，通过智能负载均衡确保服务可用性。采用SQLAlchemy ORM实现数据持久化，Alembic管理数据库迁移。系统支持多场景命名需求，满足不同用户的个性化需求。

测试结果表明，系统各项功能正常，性能表现良好，安全机制可靠。通过黑盒测试和白盒测试相结合的方法，验证了系统的稳定性和可靠性。系统已在测试环境中稳定运行，达到了预期的设计目标。

本系统的成功实现展示了现代Web框架与人工智能技术的有效结合，为智能应用开发提供了有益的参考。未来可以在以下方面进行扩展：增加更多AI模型支持、优化命名算法、添加用户社区功能等。

参 考 文 献

[1]赵飞. 基于边缘AI的环保物联网智能监测系统设计与应用[J].中国宽带,2026,22(01):155-157.DOI:10.20167/j.cnki.ISSN1673-7911.2026.01.51.
[2]沈扬. 基于AI技术的新能源发电设备智能巡检系统设计与应用[J].电力设备管理,2025,(22):158-160.DOI:10.26977/j.cnki.dlsbgl.2025.22.001.
[3]周巍. AI驱动的智慧校园安全预警系统设计与应用[J].信息与电脑,2025,37(22):131-133.
[4]任薇,杭洋,马芳. 高速公路AI云客服应答系统设计与实现[J].中国交通信息化,2025,(11):133-135+139.DOI:10.13439/j.cnki.itsc.2025.11.020.
[5]苗省,黎瑞源. 基于FastAPI与React的核心种质分析系统设计与实现[J].电脑知识与技术,2025,21(31):50-53.DOI:10.14004/j.cnki.ckt.2025.1577.
[6]张昭云.LangChain框架下基于ChatGLM3模型的个性化儿科健康咨询服务研究[D].兰州财经大学,2025.DOI:10.27732/d.cnki.gnzsx.2025.000546.
[7]宋雨蒙.面向中职的《AI智能问答的实现-基于Langchain框架》课程开发[D].贵州师范大学,2025.DOI:10.27048/d.cnki.ggzsu.2025.001412.
[8]Chelliah K S ,Arivazhagan N ,Alfarraj O , et al. Integrating LangChain and Large Language Models for Enhanced Dysarthria Speech Recognition and Communication[J].Journal of Circuits, Systems and Computers,2025,34(11):DOI:10.1142/S0218126625502342.
[9]谭舒文.基于大模型的人力资源服务问答系统设计与实现[D].西南大学,2025.DOI:10.27684/d.cnki.gxndx.2025.002707.
[10]Arun G ,Syam R ,Nair A A , et al. An integrated framework for ethical healthcare chatbots using LangChain and NeMo guardrails[J].AI and Ethics,2025,(prepublish):1-12.DOI:10.1007/S43681-025-00696-7.
[11]"AI+窗口"双核服务破解"取名难"问题[J].福建市场监督管理,2025,(02):58.
[12]万冠.基于多模态背景知识的交互问答系统设计与实现[D].哈尔滨工业大学,2025.DOI:10.27061/d.cnki.ghgdu.2025.003834.
[13]姜嘉伟.基于Langchain-LLMs框架的智能问答系统的设计与实现[D].延边大学,2024.DOI:10.27439/d.cnki.gybdu.2024.000002.

致    谢

在毕业论文完成之际，我要向所有给予我帮助和支持的老师、同学和家人表示衷心的感谢。

首先，感谢我的指导老师，在论文选题、研究过程和论文撰写过程中给予了我悉心的指导和宝贵的建议。老师的严谨治学态度和专业精神深深地影响了我，让我在学术研究中不断进步。

其次，感谢实验室的同学们，在项目开发过程中提供的技术支持和宝贵意见。通过大家的合作和交流，我学到了很多实用的技术和开发经验。

特别感谢我的家人，在我攻读学位期间给予的理解、鼓励和支持。正是家人的默默付出，让我能够专注于学业和研究。

感谢开源社区的贡献者们，本项目使用的各种开源框架和工具为我的研究提供了强大的技术支撑。

最后，感谢母校提供良好的学习环境和科研条件，让我能够在本科阶段完成这个有意义的项目。

在未来的学习和工作道路上，我将继续保持学习的热情，不断提升自己的专业能力，为社会发展贡献自己的力量。谢谢所有关心和帮助过我的人！

作者：XXX
完成日期：2025年1月15日
