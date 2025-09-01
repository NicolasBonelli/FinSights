GET /chunks_parent_fintech/_search
     {
       "query": {
         "match_all": {}
       },
       "size": 5
     }

     GET /relations_fintech/_search
     {
       "query": {
         "match_all": {}
       },
       "size": 1000
     }