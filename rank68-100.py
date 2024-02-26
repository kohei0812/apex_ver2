import function as func

start = 67
end = 99
page = func.scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=1&legend=all", start, end)

func.verify(page, start, end)
