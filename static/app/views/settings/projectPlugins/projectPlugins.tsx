import React, {Component} from 'react';
import {WithRouterProps} from 'react-router';

import Access from 'app/components/acl/access';
import Link from 'app/components/links/link';
import LoadingIndicator from 'app/components/loadingIndicator';
import {
  Panel,
  PanelAlert,
  PanelBody,
  PanelHeader,
  PanelItem,
} from 'app/components/panels';
import {t, tct} from 'app/locale';
import {Plugin, Project} from 'app/types';
import RouteError from 'app/views/routeError';

import ProjectPluginRow from './projectPluginRow';

type Props = {
  plugins: Plugin[];
  loading: boolean;
  error: React.ComponentProps<typeof RouteError>['error'];
  onChange: React.ComponentProps<typeof ProjectPluginRow>['onChange'];
  project: Project;
} & WithRouterProps<{orgId: string}>;

class ProjectPlugins extends Component<Props> {
  render() {
    const {plugins, loading, error, onChange, routes, params, project} = this.props;
    const {orgId} = this.props.params;
    const hasError = error;
    const isLoading = !hasError && loading;

    if (hasError) {
      return <RouteError error={error} />;
    }

    if (isLoading) {
      return <LoadingIndicator />;
    }

    return (
      <Panel>
        <PanelHeader>
          <div>{t('Legacy Integration')}</div>
          <div>{t('Enabled')}</div>
        </PanelHeader>
        <PanelBody>
          <PanelAlert type="warning">
            <Access access={['org:integrations']}>
              {({hasAccess}) =>
                hasAccess
                  ? tct(
                      "Legacy Integrations must be configured per-project. It's recommended to prefer organization integrations over the legacy project integrations when available. Visit the [link:organization integrations] settings to manage them.",
                      {
                        link: <Link to={`/settings/${orgId}/integrations`} />,
                      }
                    )
                  : t(
                      "Legacy Integrations must be configured per-project. It's recommended to prefer organization integrations over the legacy project integrations when available."
                    )
              }
            </Access>
          </PanelAlert>

          {plugins
            .filter(p => {
              return !p.isHidden;
            })
            .map(plugin => (
              <PanelItem key={plugin.id}>
                <ProjectPluginRow
                  params={params}
                  routes={routes}
                  project={project}
                  {...plugin}
                  onChange={onChange}
                />
              </PanelItem>
            ))}
        </PanelBody>
      </Panel>
    );
  }
}

export default ProjectPlugins;