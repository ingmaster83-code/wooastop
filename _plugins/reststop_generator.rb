require 'json'

module Jekyll
  class RestStopPageGenerator < Generator
    safe true
    priority :normal

    TYPE_LABELS = {
      "general" => "일반휴게소", "simple" => "간이휴게소", "truck" => "화물차휴게소"
    }.freeze
    TYPE_ICONS = {
      "general" => "🍽️", "simple" => "🚻", "truck" => "🚛"
    }.freeze

    def generate(site)
      stops = site.data['reststops']
      return unless stops&.any?

      Jekyll.logger.info "RestStopGenerator:", "#{stops.size}개 휴게소 페이지 생성 중..."

      stops.each do |stop|
        same_route = stops
          .select { |s| s['routeSlug'] == stop['routeSlug'] && s['slug'] != stop['slug'] }
          .first(8)
          .map { |s| { 'slug' => s['slug'], 'name' => s['stopName'], 'direction' => s['direction'], 'typeLabel' => s['typeLabel'], 'typeIcon' => s['typeIcon'] } }

        same_type = stops
          .select { |s| s['typeSlug'] == stop['typeSlug'] && s['slug'] != stop['slug'] }
          .first(8)
          .map { |s| { 'slug' => s['slug'], 'name' => s['stopName'], 'routeName' => s['routeName'] } }

        same_food = [] # 대표음식은 거의 유니크해서 그리드 대신 텍스트로만 노출

        # 이전/다음: 같은 노선 내에서 방향 -> 이름 순 정렬 후 순환
        route_ordered = stops
          .select { |s| s['routeSlug'] == stop['routeSlug'] }
          .sort_by { |s| [s['direction'].to_s, s['stopName'].to_s] }
        idx = route_ordered.index { |s| s['slug'] == stop['slug'] }
        prev_stop = nil
        next_stop = nil
        if idx && route_ordered.size > 1
          p = route_ordered[(idx - 1) % route_ordered.size]
          n = route_ordered[(idx + 1) % route_ordered.size]
          prev_stop = { 'slug' => p['slug'], 'name' => p['stopName'] }
          next_stop = { 'slug' => n['slug'], 'name' => n['stopName'] }
        end

        site.pages << RestStopPage.new(site, stop, same_route, same_type, prev_stop, next_stop)
      end

      by_route = stops.group_by { |s| s['routeSlug'] }
      by_route.each do |route_slug, route_stops|
        route_name = route_stops.first['routeName']
        site.pages << RoutePage.new(site, route_name, route_slug, route_stops)
      end

      by_type = stops.group_by { |s| s['typeSlug'] }
      by_type.each do |type_slug, type_stops|
        site.pages << TypePage.new(site, type_slug, type_stops)
      end

      site.pages << SearchIndexPage.new(site, stops)

      Jekyll.logger.info "RestStopGenerator:", "완료 (#{stops.size}개 휴게소)"
    end
  end

  class RestStopPage < Page
    def initialize(site, stop, same_route, same_type, prev_stop, next_stop)
      @site = site
      @base = site.source
      @dir  = "stop/#{stop['slug']}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'stop.html')
      self.data.merge!(stop)
      self.data['layout']      = 'stop'
      self.data['same_route']  = same_route
      self.data['same_type']   = same_type
      self.data['prev_stop']   = prev_stop
      self.data['next_stop']   = next_stop

      dir_label = stop['direction'].to_s.empty? ? '' : "(#{stop['direction']})"
      self.data['title'] = "#{stop['stopName']} 휴게소 대표음식·편의시설 | #{stop['routeName']} #{dir_label}"
      food_str = stop['food'].to_s.empty? ? '' : "대표음식: #{stop['food']}. "
      self.data['description'] = "#{stop['stopName']} 휴게소(#{stop['routeName']} #{dir_label}) 정보. #{food_str}운영시간 #{stop['openTime']}~#{stop['closeTime']}."
    end
  end

  class RoutePage < Page
    def initialize(site, route_name, slug, stops)
      @site = site
      @base = site.source
      @dir  = "route/#{slug}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'route.html')
      self.data['layout']     = 'route'
      self.data['route_name'] = route_name
      self.data['route_slug'] = slug
      self.data['stops']      = stops
      self.data['title']       = "#{route_name} 휴게소 총정리 | 전국 고속도로 휴게소 #{stops.size}곳"
      self.data['description'] = "#{route_name} 휴게소 #{stops.size}곳 총정리! 대표음식·주유소·전기차충전·화장실 등 편의시설 정보를 한눈에 확인하세요."
    end
  end

  class TypePage < Page
    def initialize(site, type_slug, stops)
      @site = site
      @base = site.source
      @dir  = "type/#{type_slug}"
      @name = 'index.html'

      label = RestStopPageGenerator::TYPE_LABELS[type_slug] || type_slug

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'type.html')
      self.data['layout']     = 'type'
      self.data['type_slug']  = type_slug
      self.data['type_label'] = label
      self.data['type_icon']  = RestStopPageGenerator::TYPE_ICONS[type_slug] || '🍽️'
      self.data['stops']      = stops
      self.data['title']       = "전국 #{label} 목록 #{stops.size}곳"
      self.data['description'] = "전국 #{label} #{stops.size}곳 목록. 노선별 휴게소 정보를 확인하세요."
    end
  end

  class SearchIndexPage < Page
    def initialize(site, stops)
      @site = site
      @base = site.source
      @dir  = ''
      @name = 'search_index.json'

      self.process(@name)
      self.data = { 'layout' => nil, 'sitemap' => false }

      index = stops.map do |s|
        {
          'slug' => s['slug'], 'name' => s['stopName'], 'routeName' => s['routeName'],
          'direction' => s['direction'], 'food' => s['food'], 'typeLabel' => s['typeLabel'],
        }
      end

      self.content = index.to_json
    end

    def output   = self.content
    def render(layouts, registers); end
  end
end
