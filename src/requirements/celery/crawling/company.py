company_to_idx = {
	'한국경제': 0,
	'세계일보': 1,
	'아시아투데이': 2,
	'조선일보': 3,
	'중앙일보': 4,
	'문화일보': 5
}

companys = {
	'한국경제': {
		'domain': 'https://www.hankyung.com',
		'items': 20,
		'article_list': 'ul.news-list > li > div.news-item > div.text-cont > h2.news-tit > a',
		'title': 'h1.headline',
		'date': 'div.datetime > span.item > span.txt-date',
		'content': 'div.article-body-wrap',
		'categories': {
			'정치': {
				'path': '/politics',
				'sub': {
					'대통령실': '/the-presidential-office',
					'국회•정당': '/the-parliament-party',
					'행정': '/governance'
				}
			},
			'경제': {
				'path': '/economy',
				'sub': {
					'경제정책': '/economic-policy',
					'거시경제': '/macro',
					'외환시장': '/forex',
					'세금': '/tax',
					'고용복지': '/job-welfare'
				}
			},
			'금융': {
				'path': '/financial-market',
				'sub': {
					'금융정책': '/financial-policy',
					'은행': '/bank',
					'보험•2금융': '/insurance-nbfis',
					'가상자산•핀테크': '/cryptocurrency-fintech',
					'재테크': '/personal-finance'
				}
			},
			'산업': {
				'path': '/industry',
				'sub': {
					'반도체•전자': '/semicon-electronics',
					'자동차•배터리': '/auto-battery',
					'조선•해운': '/ship-marine',
					'철강•화학': '/steel-chemical',
					'로봇•미래': '/robot-future',
					'경영•재계': '/manage-business'
				}
			}
		}
	},
	'세계일보': {
		'domain': 'https://www.segye.com',
		'items': 10,
		'article_list': '#wps_layout1_box1 > ul > li > a',
		'title': 'section#contTitle > h3#title_sns',
		'date': 'p.viewInfo',
		'content': 'article.viewBox2',
		'categories': {
			'정치': {
				'path': '/newsList',
				'sub': {
					'일반': '/0101010100000',
					'대통령실': '/0101010200000',
					'국회•정당': '/0101010400000',
					'선거•선관위': '/0101010500000',
					'외교•안보': '/0101010600000',
					'국방': '/0101010700000'
				}
			},
			'사회': {
				'path': '/newsList',
				'sub': {
					'일반': '/0101080100000',
					'검찰•법원': '/0101080300000',
					'노동•복지': '/0101080500000',
					'환경•날씨': '/0101080700000',
					'교통•항공': '/0101080800000',
					'교육•학교': '/0101080900000',
					'사건사고': '/0101081000000'
				}
			},
			'경제•산업': {
				'path': '/newsList',
				'sub': {
					'일반': '/0101030100000',
					'금융•증권': '/0101030300000',
					'보험': '/0101030500000',
					'부동산•건설': '/0101030700000',
					'IT•과학': '/0101030900000',
					'산업•기업': '/0101031100000',
					'자동차': '/0101031200000',
					'쇼핑•유통': '/0101031500000',
					'취업•창업': '/0101031600000'
				}
			}
		}
	},
	'조선일보': {
		'domain': 'https://www.chosun.com',
		'items': 20,
		'article_list': 'div.story-feed a.story-card__headline',
		'title': 'h1.article-header__headline > span',
		'date': 'span.upDate',
		'content': 'p.article-body__content-text',
		'categories': {
			'정치': {
				'path': '/politics',
				'sub': {
					'정치일반': '/politics_general/',
					'대통령실': '/blue_house/',
					'국회•정당': '/assembly/',
					'외교•국방': '/diplomacy-defense/',
					'행정': '/goverment/'
				}
			},
			'사회': {
				'path': '/national',
				'sub': {
					'사회일반': '/national_general/',
					'사건사고': '/incident',
					'법조': '/court_law/',
					'교육': '/education/',
					'노동': '/labor/',
					'교통•환경': '/transport-environment/'
				}
			},
			'경제': {
				'path': '/economy',
				'sub': {
					'경제일반': '/economy_general/',
					'과학': '/science/',
					'머니': '/money/'
				}
			}
		}
	},
	'중앙일보': {
		'domain': 'https://www.joongang.co.kr',
		'items': 24,
		'article_list': 'ul#story_list > li.card > div.card_body > h2.headline > a',
		'title': '#container > section > article > header > h1',
		'date': '#container > section > article > header > div.datetime > div > p:nth-child(1) > time',
		'content': '#article_body > p',
		'categories': {
			'정치': {
				'path': '/politics',
				'sub': {
					'정치일반': '/general',
					'국회•정당': '/assemgov',
					'대통령실': '/bluehouse',
					'외교': '/diplomacy',
					'국방': '/nk'
				}
			},
			'경제': {
				'path': '/money',
				'sub': {
					'경제일반': '/general',
					'경제정책': '/economicpolicy',
					'산업': '/industry',
					'금융증권': '/finance',
					'IT•과학': '/science',
					'고용노동': '/labor',
					'글로벌경제': '/globaleconomy'
				}
			},
			'사회': {
				'path': '/society',
				'sub': {
					'사회일반': '/general',
					'사건•사고': '/accident',
					'검찰•법원': '/law',
					'교육': '/education',
					'복지': '/welfare',
					'보건•질병': '/healthcare',
					'환경': '/environment',
					'교통': '/traffic',
					'전국': '/national'
				}
			}
		}
	},
	'문화일보': {
		'domain': 'https://www.munhwa.com',
		'items': 12,
		'article_list': 'div#tab01 div.card-body > h4.headline > a',
		'title': 'header.article-header > h1.title',
		'date': 'p.date-publish',
		'content': 'p.text-l',
		'categories': {
			'정치': {
				'path': '/politics',
				'sub': {
					'정치일반': '/general',
					'대통령실': '/president',
					'국회•정당': '/assembly',
					'행정': '/goverment',
					'외교': '/diplomacy',
					'국방': '/defense'
				}
			},
			'경제': {
				'path': '/economy',
				'sub': {
					'경제일반': '/general',
					'재정•재무': '/finance',
					'금융': '/money',
					'증권•주식': '/stock',
					'부동산': '/realestate',
					'무역•통상': '/trade',
					'산업•기업': '/industry',
					'유통•생활': '/circulation'
				}
			},
			'사회': {
				'path': '/society',
				'sub': {
					'사회일반': '/general',
					'사건•사고': '/incident',
					'교육•청소년': '/education',
					'환경': '/environment',
					'법원•경찰': '/law',
					'보건•의료•식품': '/medical',
					'노동•복지': '/welfare',
				}
			}
		}
	}
}